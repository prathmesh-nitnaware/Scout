import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scout.pipeline.structured_scorer import (
    calculate_structured_score,
    domain_relevance_score,
    is_ai_focused_jd,
    count_meaningful_ai_skill_matches,
)
from scout.pipeline.credibility_engine import compute_credibility
from scout.pipeline.reasoning import generate_reasoning

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
PARQUET = ARTIFACTS / "candidate_features.parquet"
EMBEDDINGS_PATH = ARTIFACTS / "embeddings.npy"
TECH_JD_EMB_PATH = ARTIFACTS / "technical_jd_embedding.npy"
JD_STRUCT_PATH = ARTIFACTS / "jd_profile_structured.json"
JD_RAW_PATH = ARTIFACTS / "jd_profile.json"

SUBMISSION_PATH = ROOT / "submission_final.csv"

def get_union_pool():
    print("[FINAL] Loading candidate features...")
    df = pd.read_parquet(PARQUET, engine="pyarrow")
    
    with open(JD_RAW_PATH, "r") as f:
        jd_raw = json.load(f)["raw_text"]
        
    print("[FINAL] Computing TF-IDF Top 1000...")
    vec = TfidfVectorizer(max_features=20000, sublinear_tf=True, min_df=2, ngram_range=(1,2), stop_words='english')
    X = vec.fit_transform(df['raw_text'])
    y = vec.transform([jd_raw])
    tf_scores = cosine_similarity(y, X).flatten()
    df["tf_score"] = tf_scores
    top_tfidf = df.sort_values("tf_score", ascending=False).head(1000)["candidate_id"].tolist()
    
    print("[FINAL] Computing Technical MiniLM Top 1000...")
    embeddings = np.load(EMBEDDINGS_PATH)
    tech_jd_emb = np.load(TECH_JD_EMB_PATH)
    ml_scores = cosine_similarity(tech_jd_emb, embeddings).flatten()
    df["ml_score"] = ml_scores
    top_minilm = df.sort_values("ml_score", ascending=False).head(1000)["candidate_id"].tolist()
    
    union_cids = set(top_tfidf).union(set(top_minilm))
    pool_df = df[df["candidate_id"].isin(union_cids)].copy()
    
    pool_df["appears_in_tfidf"] = pool_df["candidate_id"].apply(lambda x: x in top_tfidf)
    pool_df["appears_in_minilm"] = pool_df["candidate_id"].apply(lambda x: x in top_minilm)
    
    return pool_df

def main():
    pool_df = get_union_pool()
    
    with open(JD_STRUCT_PATH, "r") as f:
        jd_profile = json.load(f)
        
    print("[FINAL] Scoring Phase 4 & Phase 5...")
    results = []
    
    for _, row in pool_df.iterrows():
        cand_dict = row.to_dict()
        
        # Phase 4
        score_res = calculate_structured_score(cand_dict, jd_profile)
        base_struct_score = score_res["final_score"]
        
        # Phase 5
        cred_res = compute_credibility(cand_dict, jd_profile)
        cred_score = cred_res["credibility_score"]
        
        # Phase 3 Conf
        is_tf = row["appears_in_tfidf"]
        is_ml = row["appears_in_minilm"]
        if is_tf and is_ml:
            conf = 1.15
            retrieved_by = "BOTH"
        elif is_tf:
            conf = 1.00
            retrieved_by = "TF-IDF"
        else:
            conf = 1.00
            retrieved_by = "MiniLM"
            
        domain_relevance = domain_relevance_score(cand_dict)
        meaningful_ai_matches = count_meaningful_ai_skill_matches(cand_dict)

        # Hard safety: remove low-domain candidates that lack enough AI skill evidence
        if is_ai_focused_jd(jd_profile) and domain_relevance < 0.5 and meaningful_ai_matches < 3:
            continue

        # Combine formula: Structured * (Credibility/100) * Conf * DomainRelevance
        raw_final = base_struct_score * (cred_score / 100.0) * conf * domain_relevance
        final_score = min(100.0, raw_final) # Normalize max

        # Behavioral and Semantic scores for deterministic tie-breaking
        behavioral_score = float(row.get("activity_score", 0.0)) if pd.notna(row.get("activity_score", 0.0)) else 0.0
        semantic_score = float(row.get("ml_score", 0.0)) if pd.notna(row.get("ml_score", 0.0)) else 0.0
        
        reasoning = generate_reasoning(cand_dict, final_score, cred_res, retrieved_by, jd_profile)
        
        display_score = round(final_score / 100.0, 4)
        results.append({
            "candidate_id": row["candidate_id"],
            "current_title": row["current_title"],
            "years_exp": float(row["years_exp"]) if pd.notna(row["years_exp"]) else 0.0,
            "activity_score": behavioral_score,
            "semantic_score": semantic_score,
            "credibility_score": cred_score,
            "domain_relevance_score": domain_relevance,
            "meaningful_ai_skill_matches": meaningful_ai_matches,
            "final_score": final_score,
            "display_score": display_score,
            "reasoning": reasoning
        })
        
    res_df = pd.DataFrame(results)
    
    # For challenge submission CSV, validator requires: when displayed scores equal,
    # candidate_id must be ascending. Use display_score DESC, then candidate_id ASC.
    res_df = res_df.sort_values(
        by=["display_score", "candidate_id"],
        ascending=[False, True]
    ).reset_index(drop=True)
    res_df["rank"] = res_df.index + 1
    
    # Take exactly 100
    top100 = res_df.head(100)
    
    # Save submission_final.csv
    with open(SUBMISSION_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for _, r in top100.iterrows():
            # Pure scaling: 0.0000 - 1.0000
            s_val = round(r["final_score"] / 100.0, 4)
            writer.writerow({
                "candidate_id": r["candidate_id"],
                "rank": int(r["rank"]),
                "score": round(s_val, 4),
                "reasoning": r["reasoning"]
            })
            
    print(f"[FINAL] Saved {SUBMISSION_PATH} (100 rows)")
    
    # Stats for MD reports
    print(f"[STATS] Total Union Pool: {len(pool_df)}")
    print(f"[STATS] Top 100 Titles:")
    print(top100["current_title"].value_counts().head(5))
    
    trap1 = res_df[res_df["candidate_id"] == "CAND_0000970"]
    trap2 = res_df[res_df["candidate_id"] == "CAND_0000004"]
    print(f"[TRAP1] Data Eng: Rank {trap1.iloc[0]['rank'] if len(trap1) else 'N/A'}")
    print(f"[TRAP2] Marketing: Rank {trap2.iloc[0]['rank'] if len(trap2) else 'N/A'}")

if __name__ == "__main__":
    main()
