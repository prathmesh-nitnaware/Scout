"""
eda.py — Exploratory Data Analysis for Scout
----------------------------------------------
Reads candidate_features.parquet and generates:
    artifacts/skill_frequency.csv
    artifacts/null_analysis.csv
    artifacts/signal_stats.csv

Also prints a concise summary to stdout.

Usage:
    python scout/pipeline/eda.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
ARTIFACTS = Path(__file__).resolve().parents[2] / "artifacts"
PARQUET   = ARTIFACTS / "candidate_features.parquet"


def run_eda() -> None:
    if not PARQUET.exists():
        print(f"[ERROR] Parquet not found: {PARQUET}")
        print("  Run build_features.py first.")
        raise SystemExit(1)

    print(f"[EDA] Loading {PARQUET.name} ...")
    df = pd.read_parquet(PARQUET, engine="pyarrow")
    print(f"[EDA] Loaded {len(df):,} rows x {len(df.columns)} cols\n")

    # -----------------------------------------------------------------------
    # 1. Null / missing analysis
    # -----------------------------------------------------------------------
    print("=== NULL ANALYSIS ===")
    null_data = []
    for col in df.columns:
        if df[col].dtype == object:
            n_empty = (df[col].fillna("") == "").sum()
            n_null  = df[col].isna().sum()
        else:
            n_empty = 0
            n_null  = df[col].isna().sum()
        total_missing = n_null + n_empty
        pct = total_missing / len(df) * 100
        null_data.append({
            "column":  col,
            "dtype":   str(df[col].dtype),
            "null_count":    int(n_null),
            "empty_count":   int(n_empty),
            "total_missing": int(total_missing),
            "missing_pct":   round(pct, 2),
        })
        print(f"  {col:<36} null={n_null}  empty={n_empty}  ({pct:.1f}%)")

    null_df = pd.DataFrame(null_data).sort_values("missing_pct", ascending=False)
    null_df.to_csv(ARTIFACTS / "null_analysis.csv", index=False)
    print(f"\n  --> Saved: null_analysis.csv\n")

    # -----------------------------------------------------------------------
    # 2. Skill frequency distribution
    # -----------------------------------------------------------------------
    print("=== SKILL FREQUENCY (Top 40) ===")
    skill_counter: Counter = Counter()
    for skills_json in df["skills"]:
        try:
            skills = json.loads(skills_json) if isinstance(skills_json, str) else []
        except (json.JSONDecodeError, TypeError):
            skills = []
        for s in skills:
            name = s.get("name", "").strip()
            if name:
                skill_counter[name] += 1

    top_skills = skill_counter.most_common(200)
    for skill, count in top_skills[:40]:
        bar = "#" * int(count / len(df) * 50)
        print(f"  {skill:<35} {count:>6}  ({count/len(df)*100:.1f}%)  {bar}")

    skill_df = pd.DataFrame(top_skills, columns=["skill", "count"])
    skill_df["pct_of_candidates"] = (skill_df["count"] / len(df) * 100).round(2)
    skill_df.to_csv(ARTIFACTS / "skill_frequency.csv", index=False)
    print(f"\n  --> Saved: skill_frequency.csv ({len(skill_df)} skills)\n")

    # -----------------------------------------------------------------------
    # 3. Behavioral signal stats
    # -----------------------------------------------------------------------
    print("=== BEHAVIORAL SIGNAL STATS ===")
    signal_cols = [
        "response_rate", "activity_score",
        "recruiter_saves", "interview_completion_rate",
        "years_exp", "skills_count",
        "salary_min", "salary_max",
        "profile_completeness", "github_score",
    ]
    signal_stats = df[signal_cols].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).T
    signal_stats.columns = [str(c) for c in signal_stats.columns]
    signal_stats = signal_stats.round(4)
    print(signal_stats.to_string())
    signal_stats.to_csv(ARTIFACTS / "signal_stats.csv")
    print(f"\n  --> Saved: signal_stats.csv\n")

    # -----------------------------------------------------------------------
    # 4. Experience histogram (binned)
    # -----------------------------------------------------------------------
    print("=== EXPERIENCE DISTRIBUTION ===")
    bins = [0, 1, 2, 3, 5, 7, 10, 15, 20, 50]
    labels = ["<1yr", "1-2", "2-3", "3-5", "5-7", "7-10", "10-15", "15-20", "20+"]
    exp_dist = pd.cut(df["years_exp"], bins=bins, labels=labels, right=False)
    for label, count in exp_dist.value_counts().sort_index().items():
        bar = "#" * int(count / len(df) * 60)
        print(f"  {str(label):<8}  {count:>6}  ({count/len(df)*100:.1f}%)  {bar}")

    # -----------------------------------------------------------------------
    # 5. Country / location
    # -----------------------------------------------------------------------
    print("\n=== TOP 10 COUNTRIES ===")
    for country, cnt in df["country"].value_counts().head(10).items():
        print(f"  {str(country):<25}  {cnt:>6}  ({cnt/len(df)*100:.1f}%)")

    # -----------------------------------------------------------------------
    # 6. Education tier breakdown
    # -----------------------------------------------------------------------
    print("\n=== EDUCATION TIERS ===")
    for tier, cnt in df["education_tier"].value_counts().items():
        print(f"  {str(tier):<12}  {cnt:>6}  ({cnt/len(df)*100:.1f}%)")

    # -----------------------------------------------------------------------
    # 7. Open to work
    # -----------------------------------------------------------------------
    otw = df["open_to_work"].sum()
    print(f"\n=== OPEN TO WORK ===")
    print(f"  Yes: {otw:,} ({otw/len(df)*100:.0f}%)")
    print(f"  No:  {len(df)-otw:,} ({(len(df)-otw)/len(df)*100:.0f}%)")

    # -----------------------------------------------------------------------
    # 8. Honeypot preliminary scan (basic checks only — Phase 2 does full scan)
    # -----------------------------------------------------------------------
    print("\n=== PRELIMINARY HONEYPOT INDICATORS ===")
    # Salary inversion (min > max after our swap in build_features.py should have fixed most)
    sal_issues = df[df["salary_min"] > df["salary_max"]]
    print(f"  Salary min > max       : {len(sal_issues)}")
    # Extreme salary outliers
    sal_extreme = df[df["salary_max"] > 500]
    print(f"  Salary max > 500 LPA   : {len(sal_extreme)}")
    # Experience > 50 years
    exp_extreme = df[df["years_exp"] > 40]
    print(f"  Experience > 40 years  : {len(exp_extreme)}")
    # Zero skills
    no_skills = df[df["skills_count"] == 0]
    print(f"  Zero skills listed     : {len(no_skills)}")

    print("\n[EDA] Complete. Artifacts saved to:", ARTIFACTS)


if __name__ == "__main__":
    run_eda()
