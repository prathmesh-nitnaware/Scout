"""
technical_minilm_ranker.py
------------------------------------------------------
Pipeline:
    jd_technical_summary.txt
    -> Embed JD using all-MiniLM-L6-v2
    -> Compute cosine similarity against artifacts/embeddings.npy
    -> Filter out honeypots (validation_flags.json)
    -> Sort descending
    -> top 100 -> submission_embedding_technical.csv
    -> Save top 20 to top20_minilm_technical.csv
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
PARQUET = ARTIFACTS / "candidate_features.parquet"
EMBEDDINGS_PATH = ARTIFACTS / "embeddings.npy"
FLAGS_PATH = ARTIFACTS / "validation_flags.json"
TECH_JD_PATH = ARTIFACTS / "jd_technical_summary.txt"

OUTPUT_SUBMISSION = ARTIFACTS / "submission_embedding_technical.csv"
OUTPUT_TOP20 = ARTIFACTS / "top20_minilm_technical.csv"
MODEL_NAME = "all-MiniLM-L6-v2"


def make_reasoning(row: pd.Series, sim_score: float) -> str:
    title = row.get("current_title", "Candidate")
    yrs = row.get("years_exp", 0)
    n_skills = row.get("skills_count", 0)
    rr = row.get("response_rate", 0)
    return (
        f"{title} with {yrs:.1f} yrs; "
        f"{n_skills} skills listed; "
        f"response rate {rr:.2f}; "
        f"Technical MiniLM similarity {sim_score:.4f}."
    )


def main():
    if not PARQUET.exists() or not EMBEDDINGS_PATH.exists() or not TECH_JD_PATH.exists():
        print(f"[TECH_RANKER] Missing required files in artifacts/")
        sys.exit(1)

    jd_text = TECH_JD_PATH.read_text(encoding="utf-8")
    print(f"[TECH_RANKER] Loaded Technical JD ({len(jd_text)} chars)")

    print(f"[TECH_RANKER] Loading feature store and embeddings...")
    df = pd.read_parquet(PARQUET, engine="pyarrow")
    embeddings = np.load(EMBEDDINGS_PATH)

    # Validation flags
    if FLAGS_PATH.exists():
        with open(FLAGS_PATH, encoding="utf-8") as fh:
            flags = json.load(fh)
        valid_mask = df["candidate_id"].apply(
            lambda cid: flags.get(cid, {}).get("validation_passed", True)
        ).values
        df = df[valid_mask].reset_index(drop=True)
        embeddings = embeddings[valid_mask]

    print(f"[TECH_RANKER] Loading model '{MODEL_NAME}' to embed Tech JD...")
    model = SentenceTransformer(MODEL_NAME)
    
    # Also save the technical JD embedding explicitly
    jd_vector = model.encode([jd_text], convert_to_numpy=True)
    np.save(ARTIFACTS / "technical_jd_embedding.npy", jd_vector)

    print(f"[TECH_RANKER] Computing cosine similarities...")
    similarities = cosine_similarity(jd_vector, embeddings).flatten()

    df = df.copy()
    df["minilm_score"] = similarities

    top_candidates = (
        df.sort_values("minilm_score", ascending=False)
        .head(100)
        .reset_index(drop=True)
    )

    max_score = top_candidates["minilm_score"].iloc[0]
    min_score = top_candidates["minilm_score"].iloc[-1]
    score_range = max_score - min_score if max_score > min_score else 1.0

    rows = []
    for rank_idx, (_, row) in enumerate(top_candidates.iterrows(), start=1):
        raw_score = row["minilm_score"]
        norm_score = round(0.20 + 0.79 * (raw_score - min_score) / score_range, 4)
        rows.append({
            "candidate_id": row["candidate_id"],
            "rank": rank_idx,
            "score": norm_score,
            "reasoning": make_reasoning(row, raw_score),
            "current_title": row["current_title"],
            "years_exp": row["years_exp"],
            "raw_score": raw_score
        })

    submission_df = pd.DataFrame(rows)

    with open(OUTPUT_SUBMISSION, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        for _, row in submission_df.iterrows():
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["score"],
                "reasoning": row["reasoning"]
            })

    print(f"[TECH_RANKER] Saved {OUTPUT_SUBMISSION}")
    
    # Save Top 20 full details for benchmarking
    submission_df.head(20).to_csv(OUTPUT_TOP20, index=False)
    print(f"[TECH_RANKER] Saved {OUTPUT_TOP20}")

    print("[TECH_RANKER] Top 5 candidates:")
    for _, r in submission_df.head(5).iterrows():
        print(f"  Rank {int(r['rank'])}: {r['current_title']} ({r['years_exp']}y) | Score: {r['raw_score']:.4f}")

if __name__ == "__main__":
    main()
