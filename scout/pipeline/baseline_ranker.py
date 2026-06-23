"""
baseline_ranker.py — TF-IDF Baseline Ranker (Phase 1)
------------------------------------------------------
Pipeline:
    JD text
    -> TF-IDF vectorizer (trained on raw_text of all 100K candidates)
    -> cosine similarity between JD vector and each candidate vector
    -> sort descending
    -> top 100 -> submission.csv

This gives us a valid submission.csv immediately. Every phase after this
improves upon this baseline. The simplicity is the point — get a working
submission first, then optimize.

Usage:
    python scout/pipeline/baseline_ranker.py --jd <path_to_jd.txt>
    python scout/pipeline/baseline_ranker.py --jd <path_to_jd.txt> --output submission.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
ROOT      = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
PARQUET   = ARTIFACTS / "candidate_features.parquet"
FLAGS_PATH = ARTIFACTS / "validation_flags.json"
CHALLENGE_DIR = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"

DEFAULT_JD_PATH = CHALLENGE_DIR / "job_description.txt"   # we'll check .docx too
DEFAULT_OUTPUT  = ROOT / "submission.csv"


# ---------------------------------------------------------------------------
# Reasoning template (matches the submission.csv format from sample)
# ---------------------------------------------------------------------------

def make_reasoning(row: pd.Series, tfidf_score: float) -> str:
    """
    Produce a concise, data-driven reasoning string for each candidate.
    Template-based — zero API cost, fully reproducible.
    """
    title   = row.get("current_title", "Candidate")
    yrs     = row.get("years_exp", 0)
    n_skills = row.get("skills_count", 0)
    rr      = row.get("response_rate", 0)
    return (
        f"{title} with {yrs:.1f} yrs; "
        f"{n_skills} skills listed; "
        f"response rate {rr:.2f}; "
        f"TF-IDF similarity {tfidf_score:.4f}."
    )


# ---------------------------------------------------------------------------
# Main ranker
# ---------------------------------------------------------------------------

def rank_candidates(jd_text: str, output_path: Path) -> pd.DataFrame:
    """
    Run TF-IDF ranking against all 100K candidates in the feature store.
    Honeypots are excluded if validation_flags.json exists.
    """
    if not PARQUET.exists():
        print(f"[ERROR] Feature store not found: {PARQUET}")
        raise SystemExit(1)

    print(f"[RANKER] Loading feature store ...")
    df = pd.read_parquet(PARQUET, engine="pyarrow")
    print(f"[RANKER] {len(df):,} candidates loaded")

    # -----------------------------------------------------------------------
    # Filter out honeypots if validation flags exist
    # -----------------------------------------------------------------------
    if FLAGS_PATH.exists():
        import json
        with open(FLAGS_PATH, encoding="utf-8") as fh:
            flags = json.load(fh)
        before = len(df)
        df = df[df["candidate_id"].apply(
            lambda cid: flags.get(cid, {}).get("validation_passed", True)
        )].reset_index(drop=True)
        excluded = before - len(df)
        print(f"[RANKER] Honeypots excluded: {excluded:,} | Remaining: {len(df):,}")
    else:
        print("[RANKER] No validation_flags.json found — ranking all candidates")

    # -----------------------------------------------------------------------
    # TF-IDF vectorization
    # -----------------------------------------------------------------------
    print(f"[RANKER] Fitting TF-IDF on raw_text corpus ...")
    vectorizer = TfidfVectorizer(
        max_features=20_000,   # top 20K vocabulary terms
        sublinear_tf=True,     # log(1 + tf) — dampens very frequent terms
        min_df=2,              # ignore terms that appear in < 2 docs
        ngram_range=(1, 2),    # unigrams + bigrams
        strip_accents="unicode",
        lowercase=True,
    )
    corpus = df["raw_text"].tolist()
    tfidf_matrix = vectorizer.fit_transform(corpus)   # shape: (100K, vocab)
    print(f"[RANKER] TF-IDF matrix: {tfidf_matrix.shape}  nnz={tfidf_matrix.nnz:,}")

    # -----------------------------------------------------------------------
    # Embed the JD query
    # -----------------------------------------------------------------------
    print(f"[RANKER] Computing JD vector ...")
    jd_vector = vectorizer.transform([jd_text])       # shape: (1, vocab)

    # -----------------------------------------------------------------------
    # Cosine similarity
    # -----------------------------------------------------------------------
    print(f"[RANKER] Computing cosine similarities ...")
    similarities = cosine_similarity(jd_vector, tfidf_matrix).flatten()  # (100K,)

    df = df.copy()
    df["tfidf_score"] = similarities

    # -----------------------------------------------------------------------
    # Sort and take top 100
    # -----------------------------------------------------------------------
    top100 = (
        df.sort_values("tfidf_score", ascending=False)
        .head(100)
        .reset_index(drop=True)
    )

    # -----------------------------------------------------------------------
    # Build submission DataFrame
    # -----------------------------------------------------------------------
    # Scores must be non-increasing by rank — normalize to [0.01, 0.99]
    max_score = top100["tfidf_score"].iloc[0]
    min_score = top100["tfidf_score"].iloc[-1]
    score_range = max_score - min_score if max_score > min_score else 1.0

    rows = []
    for rank_idx, (_, row) in enumerate(top100.iterrows(), start=1):
        raw_score = row["tfidf_score"]
        # Normalize to visible range 0.2 – 0.99 (same ballpark as sample CSV)
        norm_score = round(0.20 + 0.79 * (raw_score - min_score) / score_range, 4)
        reasoning  = make_reasoning(row, raw_score)
        rows.append({
            "candidate_id": row["candidate_id"],
            "rank":         rank_idx,
            "score":        norm_score,
            "reasoning":    reasoning,
        })

    submission_df = pd.DataFrame(rows)

    # Verify scores are non-increasing
    scores = submission_df["score"].tolist()
    assert all(
        scores[i] >= scores[i + 1] for i in range(len(scores) - 1)
    ), "Scores not non-increasing — check normalization logic"

    # -----------------------------------------------------------------------
    # Write CSV (exact format required by validate_submission.py)
    # -----------------------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["candidate_id", "rank", "score", "reasoning"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[RANKER] submission.csv written: {output_path}")
    print(f"[RANKER] Top 5 candidates:")
    for _, r in submission_df.head(5).iterrows():
        print(f"  Rank {int(r['rank'])}: {r['candidate_id']}  score={r['score']}  | {r['reasoning'][:70]}...")

    return submission_df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="TF-IDF baseline ranker")
    ap.add_argument(
        "--jd",
        type=Path,
        default=None,
        help="Path to job description text file (default: tries job_description.txt in challenge dir)",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
    )
    args = ap.parse_args()

    # Resolve JD text
    jd_text: str = ""

    if args.jd is not None:
        jd_path = Path(args.jd)
        if not jd_path.exists():
            print(f"[ERROR] JD file not found: {jd_path}")
            sys.exit(1)
        jd_text = jd_path.read_text(encoding="utf-8")
        print(f"[RANKER] JD loaded from: {jd_path}  ({len(jd_text)} chars)")
    else:
        # Try to find job_description in challenge directory
        for candidate_path in [
            CHALLENGE_DIR / "job_description.txt",
            CHALLENGE_DIR / "job_description.md",
        ]:
            if candidate_path.exists():
                jd_text = candidate_path.read_text(encoding="utf-8")
                print(f"[RANKER] JD auto-found: {candidate_path}  ({len(jd_text)} chars)")
                break

        if not jd_text:
            # Fallback: use a hardcoded representative JD for the hackathon
            print("[RANKER] No JD file found — using hardcoded ML Engineer JD for Phase 1 baseline")
            jd_text = (
                "We are looking for a Senior Machine Learning Engineer with 5+ years of experience "
                "building production ML systems. Required skills: Python, PyTorch or TensorFlow, "
                "scikit-learn, NLP, LLM fine-tuning, FAISS or vector databases, REST API development. "
                "Experience with MLOps, model deployment, and cloud platforms (AWS or GCP) is required. "
                "Strong understanding of deep learning, transformers, BERT, GPT architectures. "
                "Data engineering background with Spark, Airflow, or Kafka is a strong plus. "
                "Location: Bangalore or remote. Min 3 years in a senior or lead ML role."
            )

    rank_candidates(jd_text, args.output)


if __name__ == "__main__":
    main()
