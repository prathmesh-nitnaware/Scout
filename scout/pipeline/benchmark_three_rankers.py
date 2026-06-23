"""
benchmark_three_rankers.py
------------------------------------------------------
Compare A) TF-IDF, B) MiniLM Full, C) MiniLM Tech
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
SUB_TFIDF = ROOT / "submission.csv"
SUB_MINILM_FULL = ROOT / "submission_embedding.csv"
SUB_MINILM_TECH = ARTIFACTS / "submission_embedding_technical.csv"
TOP20_TECH = ARTIFACTS / "top20_minilm_technical.csv"

def get_overlap(df1, df2, k):
    s1 = set(df1.head(k)["candidate_id"])
    s2 = set(df2.head(k)["candidate_id"])
    return len(s1.intersection(s2))

def main():
    df_tf = pd.read_csv(SUB_TFIDF)
    df_ml_full = pd.read_csv(SUB_MINILM_FULL)
    df_ml_tech = pd.read_csv(SUB_MINILM_TECH)
    
    # Check overlap with TF-IDF
    print("=" * 60)
    print("OVERLAP WITH TF-IDF BASELINE")
    print("=" * 60)
    for k in [10, 20, 100]:
        o_full = get_overlap(df_tf, df_ml_full, k)
        o_tech = get_overlap(df_tf, df_ml_tech, k)
        print(f"Top {k:>3}: MiniLM (Full) = {o_full:>2} | MiniLM (Tech) = {o_tech:>2}")
    
    # Print the Top 10 from MiniLM Tech to see if the titles are better
    print("\n" + "=" * 60)
    print("MINILM (TECHNICAL JD) - TOP 10 CANDIDATES")
    print("=" * 60)
    df_tech_details = pd.read_csv(TOP20_TECH)
    for i, row in df_tech_details.head(10).iterrows():
        print(f"Rank {row['rank']:>2}: {row['current_title']:<30} | Exp: {row['years_exp']}y")

if __name__ == "__main__":
    main()
