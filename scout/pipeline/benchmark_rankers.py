"""
benchmark_rankers.py — Compare TF-IDF Baseline vs MiniLM
--------------------------------------------------------
Computes overlap at Top 20, Top 50, and Top 100 between the TF-IDF submission
and the MiniLM submission.

Usage:
    python scout/pipeline/benchmark_rankers.py
"""

import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
SUB_TFIDF = ROOT / "submission.csv"
SUB_MINILM = ROOT / "submission_embedding.csv"
REPORT_JSON = ARTIFACTS / "benchmark_report.json"
TOP20_TFIDF_CSV = ARTIFACTS / "top20_tfidf.csv"
TOP20_MINILM_CSV = ARTIFACTS / "top20_minilm.csv"

def print_overlap(df_tf, df_ml, k):
    top_tf = set(df_tf.head(k)["candidate_id"])
    top_ml = set(df_ml.head(k)["candidate_id"])
    
    overlap = len(top_tf.intersection(top_ml))
    print(f"Top {k:>3} Overlap : {overlap:>3} / {k} ({overlap/k*100:.1f}%)")
    return top_tf, top_ml

def main():
    if not SUB_TFIDF.exists():
        print(f"[BENCHMARK] Missing TF-IDF submission at {SUB_TFIDF}")
        return
    if not SUB_MINILM.exists():
        print(f"[BENCHMARK] Missing MiniLM submission at {SUB_MINILM}")
        return

    print("Loading submissions...")
    df_tf = pd.read_csv(SUB_TFIDF)
    df_ml = pd.read_csv(SUB_MINILM)
    
    # Merge reasoning for inspection
    df_tf_merged = df_tf.set_index("candidate_id")
    df_ml_merged = df_ml.set_index("candidate_id")

    print("\n" + "="*50)
    print("RANKING OVERLAP: TF-IDF vs MiniLM")
    print("="*50)
    
    t20_tf, t20_ml = print_overlap(df_tf, df_ml, 20)
    t50_tf, t50_ml = print_overlap(df_tf, df_ml, 50)
    t100_tf, t100_ml = print_overlap(df_tf, df_ml, 100)
    
    report = {
        "overlap_top20": len(t20_tf.intersection(t20_ml)),
        "overlap_top50": len(t50_tf.intersection(t50_ml)),
        "overlap_top100": len(t100_tf.intersection(t100_ml)),
        "new_in_top20_minilm": [],
        "dropped_from_top20_tfidf": []
    }
    
    print("\n" + "="*50)
    print("NEW IN TOP 20 (Found by MiniLM, missed by TF-IDF)")
    print("="*50)
    new_in_ml = t20_ml - t20_tf
    for cid in new_in_ml:
        rank = df_ml_merged.loc[cid, "rank"]
        reason = df_ml_merged.loc[cid, "reasoning"]
        print(f"Rank {rank:>2}: {cid} -> {reason}")
        report["new_in_top20_minilm"].append({"candidate_id": cid, "rank": int(rank), "reasoning": str(reason)})

    print("\n" + "="*50)
    print("DROPPED FROM TOP 20 (Found by TF-IDF, missed by MiniLM)")
    print("="*50)
    dropped_from_tf = t20_tf - t20_ml
    for cid in dropped_from_tf:
        rank = df_tf_merged.loc[cid, "rank"]
        reason = df_tf_merged.loc[cid, "reasoning"]
        print(f"Rank {rank:>2}: {cid} -> {reason}")
        report["dropped_from_top20_tfidf"].append({"candidate_id": cid, "rank": int(rank), "reasoning": str(reason)})

    # Save outputs
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[BENCHMARK] Saved {REPORT_JSON}")

    df_tf.head(20).to_csv(TOP20_TFIDF_CSV, index=False)
    print(f"[BENCHMARK] Saved {TOP20_TFIDF_CSV}")

    df_ml.head(20).to_csv(TOP20_MINILM_CSV, index=False)
    print(f"[BENCHMARK] Saved {TOP20_MINILM_CSV}")

if __name__ == "__main__":
    main()
