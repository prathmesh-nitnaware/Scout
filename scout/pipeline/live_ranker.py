"""
live_ranker.py — Production-grade Scout Ranking Engine
"""

import re
import time
import json
import logging
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from scout.pipeline.jd_parser import parse_jd
from scout.pipeline.structured_scorer import (
    calculate_structured_score,
    domain_relevance_score,
    is_ai_focused_jd,
    count_meaningful_ai_skill_matches,
)
from scout.pipeline.credibility_engine import compute_credibility, format_credibility
from scout.pipeline.reasoning import generate_reasoning

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Experience Extraction
# ---------------------------------------------------------------------------

_EXP_PATTERNS = [
    (r"(\d+)\s*(?:-|–|to)\s*(\d+)\s+years?", "range"),
    (r"(\d+)\+\s*years?", "plus"),
    (r"(?:minimum|at least|min)\s+(?:of\s+)?(\d+)\s+years?", "min_only"),
    (r"(\d+)\s+years?\s+(?:of\s+)?experience", "exact"),
]

def extract_experience_bounds(jd_text: str) -> dict:
    text_lower = jd_text.lower()
    
    for pattern, kind in _EXP_PATTERNS:
        match = re.search(pattern, text_lower)
        if not match:
            continue
        
        if kind == "range":
            lo, hi = int(match.group(1)), int(match.group(2))
            return {"min_years": lo, "max_years": hi}
        
        elif kind == "plus":
            lo = int(match.group(1))
            return {"min_years": lo, "max_years": lo + 5} 
        
        elif kind == "min_only":
            lo = int(match.group(1))
            return {"min_years": lo, "max_years": lo + 6}
        
        elif kind == "exact":
            val = int(match.group(1))
            return {"min_years": max(0, val - 2), "max_years": val + 2}
    
    return {"min_years": 5, "max_years": 9}


# ---------------------------------------------------------------------------
# Technical JD Text for MiniLM
# ---------------------------------------------------------------------------

def build_technical_jd_text(jd_profile: dict, raw_jd_text: str = "") -> str:
    lines = []

    role = jd_profile.get("role_title") or jd_profile.get("title") or ""
    if role:
        lines.append(f"Role: {role}")

    min_y = jd_profile.get("min_years", 5)
    max_y = jd_profile.get("max_years", 9)
    lines.append(f"Experience: {min_y}-{max_y} years")

    req = jd_profile.get("required_skills", [])
    if req:
        lines.append("Required Skills:\n" + "\n".join(req[:12]))

    pref = jd_profile.get("preferred_skills", [])
    if pref:
        lines.append("Preferred Skills:\n" + "\n".join(pref[:8]))

    resp = jd_profile.get("responsibilities", [])
    if resp:
        lines.append("Responsibilities:\n" + "\n".join(resp[:6]))

    if len(lines) <= 1 or (not req and not pref and not resp):
        if not req and raw_jd_text:
            logger.warning("JD Parser returned no required skills. Falling back to raw text chunk for MiniLM embedding.")
            lines.append(f"Raw Job Description Context:\n{raw_jd_text[:1000]}")
        else:
            lines.append("Required Skills:\n" + "\n".join(req))

    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Main Ranking Function
# ---------------------------------------------------------------------------

def rank_candidates(jd_text: str, cache: dict, top_k: int = 100) -> dict:
    start_time = time.time()

    jd_profile = parse_jd(jd_text)

    print("\n===== JD PROFILE =====")
    print(json.dumps(jd_profile, indent=2))
    print("======================\n")

    exp_bounds = extract_experience_bounds(jd_text)
    jd_profile["min_years"] = exp_bounds["min_years"]
    jd_profile["max_years"] = exp_bounds["max_years"]

    df = cache["df"]
    embeddings = cache["embeddings"]
    tfidf_vec = cache["tfidf_vec"]
    tfidf_matrix = cache["tfidf_matrix"]
    model = cache["model"]

    # TF-IDF
    y_tfidf = tfidf_vec.transform([jd_text])
    tf_scores_arr = cosine_similarity(y_tfidf, tfidf_matrix).flatten()
    tf_sorted_idx = np.argsort(tf_scores_arr)[::-1][:1000]
    top_tfidf_ids = df.iloc[tf_sorted_idx]["candidate_id"].tolist()
    tf_rank_map = {cid: rank + 1 for rank, cid in enumerate(top_tfidf_ids)}
    top_tfidf_set = set(top_tfidf_ids)

    # MiniLM
    tech_jd_text = build_technical_jd_text(jd_profile, jd_text)
    logger.debug(f"Generated Tech JD Text for MiniLM: {tech_jd_text}")
    
    jd_vector = model.encode([tech_jd_text], convert_to_numpy=True)
    ml_scores_arr = cosine_similarity(jd_vector, embeddings).flatten()

    ml_sorted_idx = np.argsort(ml_scores_arr)[::-1][:1000]
    top_minilm_ids = df.iloc[ml_sorted_idx]["candidate_id"].tolist()
    ml_rank_map = {cid: rank + 1 for rank, cid in enumerate(top_minilm_ids)}
    top_minilm_set = set(top_minilm_ids)

    # Union Pool
    union_cids = top_tfidf_set.union(top_minilm_set)
    union_idx = df.index[df["candidate_id"].isin(union_cids)]
    pool_df = df.loc[union_idx]

    results = []
    for _, row in pool_df.iterrows():
        cand_dict = row.to_dict()
        if isinstance(cand_dict.get("skills"), str):
            try:
                cand_dict["skills_list"] = json.loads(cand_dict["skills"])
            except Exception:
                cand_dict["skills_list"] = []

        score_res = calculate_structured_score(cand_dict, jd_profile)
        base_struct_score = score_res["final_score"]
        # Extracted breakdown for debug
        breakdown = score_res.get("breakdown", {})

        cred_res = compute_credibility(cand_dict, jd_profile)
        cred_score = cred_res["credibility_score"]

        cid = row["candidate_id"]
        is_tf = cid in top_tfidf_set
        is_ml = cid in top_minilm_set

        if is_tf and is_ml:
            tf_r = tf_rank_map.get(cid, 1000)
            ml_r = ml_rank_map.get(cid, 1000)
            geo_rank = (tf_r * ml_r) ** 0.5
            conf = 1.10 + 0.10 * max(0.0, (500 - geo_rank) / 500)
            conf = min(1.20, max(1.10, conf)) 
            retrieved_by = "BOTH"
        elif is_tf:
            conf = 1.00
            retrieved_by = "TF-IDF"
        else:
            conf = 1.00
            retrieved_by = "MiniLM"

        domain_relevance = domain_relevance_score(cand_dict)
        meaningful_ai_matches = count_meaningful_ai_skill_matches(cand_dict)

        raw_final = base_struct_score * (cred_score / 100.0) * conf * domain_relevance
        final_score = min(100.0, raw_final)

        # Title relevance multiplier applied AFTER aggregate scoring (per reviewer request)
        title = str(row.get("current_title", "")).lower()
        target_role = str(jd_profile.get("role_title", "")).lower()

        ai_titles = [
            "ai engineer", "machine learning engineer", "ml engineer",
            "applied scientist", "data scientist", "genai engineer",
            "llm engineer", "nlp engineer"
        ]
        software_titles = ["software engineer", "backend engineer", "full stack engineer", "full-stack engineer", "fullstack engineer"]
        low_titles = ["devops engineer", "site reliability engineer", "sre", "qa engineer", "support engineer"]

        title_multiplier = 1.0
        if any(t in title for t in ai_titles) or any(t in target_role for t in ai_titles):
            title_multiplier = 1.00
        elif any(t in title for t in software_titles) or any(t in target_role for t in software_titles):
            title_multiplier = 0.90
        elif any(t in title for t in low_titles) or any(t in target_role for t in low_titles):
            title_multiplier = 0.75

        # Apply multiplier (small adjustment) and clamp
        final_score = min(100.0, final_score * title_multiplier)

        # Behavioral score (activity-based)
        behavioral_score = float(row.get("activity_score", 0.0)) if pd.notna(row.get("activity_score", 0.0)) else 0.0

        # Semantic score: map df index -> ml_scores_arr position
        try:
            pos = df.index.get_loc(row.name)
            semantic_score = float(ml_scores_arr[pos]) if pos < len(ml_scores_arr) else 0.0
        except Exception:
            semantic_score = 0.0

        reasoning = generate_reasoning(cand_dict, final_score, cred_res, retrieved_by, jd_profile)

        results.append({
            "candidate_id": cid,
            "current_title": row["current_title"],
            "years_exp": float(row["years_exp"]) if pd.notna(row["years_exp"]) else 0.0,
            "activity_score": float(row.get("activity_score", 0.0)) if pd.notna(row.get("activity_score", 0.0)) else 0.0,
            "final_score": final_score,
            "credibility_score": cred_score,
            "behavioral_score": behavioral_score,
            "semantic_score": semantic_score,
            "domain_relevance_score": domain_relevance,
            "meaningful_ai_skill_matches": meaningful_ai_matches,
            "retrieved_by": retrieved_by,
            "reasoning": reasoning,
            "breakdown": breakdown
        })

    # Before sorting, handle AI-specific required-skill validation (Issue 4)
    # Build required skill list and generic skills
    required_skills = [s.lower() for s in jd_profile.get("required_skills", [])]
    generic_skills = set(["python", "git", "linux", "sql"])

    # Hard safety: filter out low-domain candidates with insufficient AI skill evidence
    if is_ai_focused_jd(jd_profile):
        pre_filter_len = len(results)
        results = [
            r for r in results
            if not (
                r["domain_relevance_score"] < 0.5
                and r["meaningful_ai_skill_matches"] < 3
            )
        ]
        logger.debug(f"Excluded {pre_filter_len - len(results)} low-domain AI candidates before final ranking.")

    # Annotate non-generic skill matches per candidate
    for r in results:
        try:
            orig_row = df[df["candidate_id"] == r["candidate_id"]].iloc[0]
            skills_field = orig_row.get("skills_list") or orig_row.get("skills") or []
        except Exception:
            skills_field = []

        cand_skill_names = set()
        if isinstance(skills_field, str):
            try:
                skills_field = json.loads(skills_field)
            except Exception:
                skills_field = []

        if isinstance(skills_field, list):
            for s in skills_field:
                if isinstance(s, dict):
                    name = s.get("name") or s.get("skill_name") or ""
                else:
                    name = str(s)
                if name:
                    cand_skill_names.add(name.lower())

        meaningful = 0
        for req in required_skills:
            for cs in cand_skill_names:
                if req in cs or cs in req:
                    if req not in generic_skills and cs not in generic_skills:
                        meaningful += 1
        r["non_generic_skill_matches"] = meaningful

    res_df = pd.DataFrame(results)

    # Fallback rule (Issue 5): If required_skills is empty, disable non_generic_skill_matches filter
    # This prevents zero-candidate results for generic role JDs like Backend Developer
    has_skill_constraints = len(required_skills) > 0

    # If pool is larger than top_k, exclude candidates with zero meaningful AI matches
    # BUT: only if JD has defined required_skills (i.e. the JD has explicit skill constraints)
    if has_skill_constraints and len(res_df) > top_k:
        pre_filter_len = len(res_df)
        res_df = res_df[res_df["non_generic_skill_matches"] > 0]
        logger.debug(f"Excluded {pre_filter_len - len(res_df)} candidates with only generic skills (Python-only).")
    elif has_skill_constraints:
        # Apply severe penalty to candidates with zero non-generic matches (if JD has required skills)
        for idx, row in enumerate(res_df.to_dict("records")):
            if row.get("non_generic_skill_matches", 0) == 0:
                res_df.loc[res_df["candidate_id"] == row["candidate_id"], "final_score"] = res_df.loc[res_df["candidate_id"] == row["candidate_id"], "final_score"] * 0.5

    # Deterministic sorting (Issue 3): final -> behavioral -> semantic -> credibility -> candidate_id
    res_df = res_df.sort_values(
        by=["final_score", "behavioral_score", "semantic_score", "credibility_score", "candidate_id"],
        ascending=[False, False, False, False, True]
    ).reset_index(drop=True)
    res_df["rank"] = res_df.index + 1

    top_candidates = res_df.head(top_k)

    # Change C: Debug Print for Top 10 Candidates
    print(f"\n[RANKER DEBUG] Top 10 Scoring Breakdown for {jd_profile.get('role_title')}:")
    print("-" * 100)
    for _, r in top_candidates.head(10).iterrows():
        bd = r['breakdown']
        title = r['current_title']
        if len(title) > 30: title = title[:27] + "..."
        print(f"{title:<30} | Role: {bd.get('career', 0):.2f} | Skills: {bd.get('skills', 0):.2f} | Exp: {bd.get('experience', 0):.2f} | Final: {r['final_score']:>6.2f}")
    print("-" * 100 + "\n")

    candidates_out = []
    for _, r in top_candidates.iterrows():
        candidates_out.append({
            "candidate_id": r["candidate_id"],
            "rank": int(r["rank"]),
            "score": round(r["final_score"] / 100.0, 4),
            "reasoning": r["reasoning"],
            "current_title": r["current_title"],
            "years_exp": r["years_exp"],
            "credibility": format_credibility(r["credibility_score"]),
        })

    runtime = round(time.time() - start_time, 2)

    both_count = sum(1 for r in results if r["retrieved_by"] == "BOTH")
    tfidf_only = sum(1 for r in results if r["retrieved_by"] == "TF-IDF")
    ml_only = sum(1 for r in results if r["retrieved_by"] == "MiniLM")

    return {
        "status": "success",
        "runtime_seconds": runtime,
        "candidate_count": len(candidates_out),
        "jd_experience_parsed": exp_bounds,
        "retrieval_stats": {
            "tfidf_pool_size": len(top_tfidf_set),
            "minilm_pool_size": len(top_minilm_set),
            "union_pool_size": len(union_cids),
            "both_retrieved": both_count,
            "tfidf_only": tfidf_only,
            "minilm_only": ml_only,
        },
        "candidates": candidates_out,
    }