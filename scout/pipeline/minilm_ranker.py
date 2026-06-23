"""
minilm_ranker.py — MiniLM Embeddings Ranker (Phase 3)
------------------------------------------------------
Pipeline:
    jd_profile.json
    -> Extract Technical JD using build_technical_jd_text
    -> Embed Technical JD using all-MiniLM-L6-v2
    -> Compute cosine similarity against artifacts/embeddings.npy (Future: FAISS/ANN)
    -> Filter out honeypots (validation_flags.json)
    -> Sort descending
    -> top 100 -> submission_embedding.csv

Usage:
    python scout/pipeline/minilm_ranker.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Change 1: Import the centralized technical JD builder
try:
    from scout.pipeline.live_ranker import build_technical_jd_text
except ImportError:
    print("[RANKER] ERROR: scout.pipeline.live_ranker not found. Ensure scout is in PYTHONPATH.")
    sys.exit(1)

# ---------------------------------------------------------------------------
ROOT      = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
PARQUET   = ARTIFACTS / "candidate_features.parquet"
EMBEDDINGS_PATH = ARTIFACTS / "embeddings.npy"
FLAGS_PATH = ARTIFACTS / "validation_flags.json"
JD_PROFILE_PATH = ARTIFACTS / "jd_profile.json"

DEFAULT_OUTPUT  = ROOT / "submission_embedding.csv"
MODEL_NAME = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
def make_reasoning(row: pd.Series, sim_score: float) -> str:
    title   = row.get("current_title", "Candidate")
    yrs     = row.get("years_exp", 0)
    n_skills = row.get("skills_count", 0)
    rr      = row.get("response_rate", 0)
    return (
        f"{title} with {yrs:.1f} yrs; "
        f"{n_skills} skills listed; "
        f"response rate {rr:.2f}; "
        f"MiniLM similarity {sim_score:.4f}."
    )

def rank_candidates(jd_profile: dict, output_path: Path, top_n: int = 100, model=None) -> pd.DataFrame:
    if not PARQUET.exists() or not EMBEDDINGS_PATH.exists():
        print(f"[RANKER] ERROR: Parquet or embeddings.npy not found.")
        sys.exit(1)

    print(f"[RANKER] Loading feature store...")
    df = pd.read_parquet(PARQUET, engine="pyarrow")
    
    print(f"[RANKER] Loading embeddings...")
    embeddings = np.load(EMBEDDINGS_PATH)
    
    # Validation flags
    if FLAGS_PATH.exists():
        with open(FLAGS_PATH, encoding="utf-8") as fh:
            flags = json.load(fh)
        
        # We need a boolean mask to filter both df and embeddings
        valid_mask = df["candidate_id"].apply(
            lambda cid: flags.get(cid, {}).get("validation_passed", True)
        ).values
        
        df = df[valid_mask].reset_index(drop=True)
        embeddings = embeddings[valid_mask]
        print(f"[RANKER] Honeypots excluded. Remaining valid candidates: {len(df):,}")
    else:
        print("[RANKER] No validation flags found. Ranking all 100K.")

    # Change 1 & 2: Build the dense technical context instead of embedding raw text
    raw_text = jd_profile.get("raw_text", "")
    jd_text = build_technical_jd_text(jd_profile, raw_text)
    
    # Change 4: Allow model to be passed in from cache, otherwise load it
    if model is None:
        print(f"[RANKER] Loading model '{MODEL_NAME}' to embed JD...")
        model = SentenceTransformer(MODEL_NAME)
        
    jd_vector = model.encode([jd_text], convert_to_numpy=True)

    print(f"[RANKER] Computing cosine similarities...")
    # Change 6 Note: Full array dot product. Valid for 100K. FAISS/HNSW recommended for >500K.
    similarities = cosine_similarity(jd_vector, embeddings).flatten()
    
    df = df.copy()
    df["minilm_score"] = similarities

    # Sort
    top_candidates = (
        df.sort_values("minilm_score", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    rows = []
    for rank_idx, (_, row) in enumerate(top_candidates.iterrows(), start=1):
        raw_score = float(row["minilm_score"])
        # Change 3: Replaced arbitrary dynamic normalization with raw cosine boundaries
        norm_score = round(raw_score, 4)
        
        rows.append({
            "candidate_id": row["candidate_id"],
            "rank":         rank_idx,
            "score":        norm_score,
            "reasoning":    make_reasoning(row, raw_score),
            "raw_score":    raw_score,
            "current_title": row.get("current_title", "Unknown"),
            "years_exp":    float(row.get("years_exp", 0.0))
        })

    submission_df = pd.DataFrame(rows)

    # Change 5: Retrieval Analysis for debugging query quality
    avg_exp = submission_df["years_exp"].mean()
    top_titles = submission_df["current_title"].value_counts().head(3).to_dict()
    
    print(f"\n[RANKER] Retrieval Analysis (Top {top_n}):")
    print(f"  Avg Experience : {avg_exp:.1f} years")
    print(f"  Top Titles     : {top_titles}")

    # Write the CSV format for validation
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["candidate_id", "rank", "score", "reasoning"],
        )
        writer.writeheader()
        for _, row in submission_df.iterrows():
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["score"],
                "reasoning": row["reasoning"]
            })

    print(f"\n[RANKER] {output_path.name} written with top {top_n} candidates.")
    print(f"[RANKER] Top 10 candidates:")
    for _, r in submission_df.head(10).iterrows():
        print(f"  Rank {int(r['rank']):>2}: {r['candidate_id']} | Score: {r['raw_score']:.4f} | {r['current_title']} ({r['years_exp']}y)")

    return submission_df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--top_n", type=int, default=100)
    args = ap.parse_args()

    if not JD_PROFILE_PATH.exists():
        print(f"[ERROR] {JD_PROFILE_PATH} not found. Run extract_jd.py first.")
        sys.exit(1)
        
    with open(JD_PROFILE_PATH, encoding="utf-8") as f:
        jd_profile = json.load(f)
        
    print(f"[RANKER] Loaded JD Profile for role: {jd_profile.get('role_title', 'Unknown')}")
    
    # Passes the full dict to utilize build_technical_jd_text cleanly
    rank_candidates(jd_profile, args.output, top_n=args.top_n)

if __name__ == "__main__":
    main()