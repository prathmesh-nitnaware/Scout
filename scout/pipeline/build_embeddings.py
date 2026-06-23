"""
build_embeddings.py — Generate MiniLM embeddings for candidates
---------------------------------------------------------------
Uses sentence-transformers (all-MiniLM-L6-v2) to embed candidates.
Per the user's direction, we embed a structured combination of:
  - title
  - years_exp
  - education
  - github_score
  - skills (newline separated for higher attention weighting)
  - summary (truncated)
  - career_text (truncated to avoid context window overflow)

Outputs:
    artifacts/embeddings.npy

Usage:
    python scout/pipeline/build_embeddings.py
    python scout/pipeline/build_embeddings.py --limit 1000  # for testing
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
PARQUET_PATH = ARTIFACTS / "candidate_features.parquet"
EMBEDDINGS_OUT = ARTIFACTS / "embeddings.npy"
MODEL_NAME = "all-MiniLM-L6-v2"

def construct_embed_text(row: pd.Series) -> str:
    """
    Construct an optimized text block for MiniLM embedding.
    Front-loads high-signal features (Title, Exp, Edu, Skills) before 
    potentially overflowing the token window with long narratives.
    """
    # Change 1: Extract title and experience
    title = str(row.get("current_title", "")).strip()
    yoe = float(row.get("years_exp", 0.0)) if pd.notna(row.get("years_exp")) else 0.0
    
    # Change 3: Extract education signal
    degree = str(row.get("highest_degree", "")).strip()
    field = str(row.get("education_field", "")).strip()
    edu_str = f"{degree} {field}".strip()

    # Change 4: Extract GitHub score
    github_score = float(row.get("github_score", 0.0)) if pd.notna(row.get("github_score")) else 0.0
    
    # Change 2: Explicit newline-separated skill weighting
    try:
        skills_data = json.loads(row.get("skills", "[]"))
        skill_names = [str(s.get("name", "")).strip() for s in skills_data if s.get("name")]
        skills_str = "\n".join(skill_names)
    except Exception:
        skills_str = ""

    # Change 1: Truncate long narratives to preserve context window
    summary = str(row.get("summary", "")).strip()[:1000]
    career_text = str(row.get("career_text", "")).strip()[:2000]

    # Assemble sequence to prioritize absolute rank features
    parts = []
    
    if title:
        parts.append(f"Title: {title}")
    if yoe > 0:
        parts.append(f"Experience: {yoe:.1f} years")
    if edu_str:
        parts.append(f"Education: {edu_str}")
    if github_score > 0:
        parts.append(f"GitHub Score: {github_score}")
    if skills_str:
        parts.append(f"Skills:\n{skills_str}")
    if summary:
        parts.append(f"Summary:\n{summary}")
    if career_text:
        parts.append(f"Career History:\n{career_text}")

    # Use double newlines to create clear semantic breaks for the transformer
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="Limit number of rows for testing")
    args = ap.parse_args()

    print(f"[EMBED] Loading candidates from {PARQUET_PATH.name}...")
    df = pd.read_parquet(PARQUET_PATH, engine="pyarrow")
    if args.limit:
        df = df.head(args.limit)
        print(f"[EMBED] Test mode: limited to {args.limit} rows.")
    print(f"[EMBED] Total candidates to process: {len(df):,}")

    print(f"[EMBED] Constructing optimized text corpus...")
    # It's faster to do this in a vectorized/apply way
    corpus = df.apply(construct_embed_text, axis=1).tolist()
    
    print(f"[EMBED] Loading SentenceTransformer model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"[EMBED] Generating embeddings (this may take a few minutes for 100K)...")
    # batch_size=256 or 512 is good for CPU/GPU. MiniLM is quite fast.
    embeddings = model.encode(
        corpus, 
        batch_size=256, 
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print(f"[EMBED] Embeddings shape: {embeddings.shape}, dtype: {embeddings.dtype}")
    
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_OUT, embeddings)
    print(f"[EMBED] Saved embeddings to {EMBEDDINGS_OUT} ({(EMBEDDINGS_OUT.stat().st_size / 1024 / 1024):.1f} MB)")

if __name__ == "__main__":
    main()