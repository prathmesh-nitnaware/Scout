"""
build_features.py — Candidate Feature Store Builder
----------------------------------------------------
Reads the raw candidates.jsonl (100K records) and produces
artifacts/candidate_features.parquet — a compact, typed, analysis-ready
feature store with one row per candidate.

Run once on Day 1, then EVERY downstream module reads from parquet.

Final columns (per user spec):
    candidate_id, years_exp, current_title, location, country,
    skills (JSON str), skills_count, education_tier, highest_degree,
    education_text, summary, career_text, raw_text,
    response_rate, activity_score, recruiter_saves, interview_completion_rate,
    salary_min, salary_max

Plus auxiliary:
    education_field, num_jobs, open_to_work, willing_to_relocate,
    preferred_work_mode, notice_period_days, profile_completeness,
    github_score

Usage:
    python scout/pipeline/build_features.py
    python scout/pipeline/build_features.py --limit 1000   # quick test
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"
DEFAULT_JSONL = (
    ROOT
    / "[PUB] India_runs_data_and_ai_challenge"
    / "India_runs_data_and_ai_challenge"
    / "candidates.jsonl"
)
OUTPUT_PARQUET = ARTIFACTS_DIR / "candidate_features.parquet"

REFERENCE_DATE = date(2026, 6, 18)  # today

# Tier ordering: tier_1 is best
TIER_ORDER = ["tier_1", "tier_2", "tier_3", "tier_4", "unknown"]

# Degree normalisation lookup
DEGREE_NORM: dict[str, str] = {
    "ph.d": "PhD", "phd": "PhD", "ph.d.": "PhD",
    "doctorate": "PhD", "doctor": "PhD",
    "m.tech": "Masters", "m.e.": "Masters", "m.sc": "Masters",
    "m.s.": "Masters", "mba": "Masters", "m.b.a": "Masters",
    "m.eng": "Masters", "master": "Masters", "m.ca": "Masters",
    "m.com": "Masters", "mtech": "Masters", "me": "Masters",
    "b.tech": "Bachelors", "b.e.": "Bachelors", "b.sc": "Bachelors",
    "b.s.": "Bachelors", "bachelor": "Bachelors", "b.com": "Bachelors",
    "b.ca": "Bachelors", "b.eng": "Bachelors", "be": "Bachelors",
    "btech": "Bachelors", "b.tech.": "Bachelors",
    "associate": "Associate", "diploma": "Associate",
}


# ---------------------------------------------------------------------------
# Null-safe helpers
# ---------------------------------------------------------------------------

def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


def safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Field extractors
# ---------------------------------------------------------------------------

def normalize_degree(raw: str) -> str:
    if not raw:
        return "Other"
    lowered = raw.strip().lower().rstrip(".")
    for key, norm in DEGREE_NORM.items():
        if lowered.startswith(key):
            return norm
    return "Other"


def best_education(edu_list: list[dict]) -> dict:
    """Pick the highest-tier (tier_1 best) education record."""
    if not edu_list:
        return {"tier": "unknown", "degree": "Other", "field": ""}

    def rank(e: dict) -> tuple:
        tier = e.get("tier", "unknown")
        tier_rank = TIER_ORDER.index(tier) if tier in TIER_ORDER else 99
        return (tier_rank, -(e.get("end_year") or 0))

    best = sorted(edu_list, key=rank)[0]
    return {
        "tier":   best.get("tier", "unknown"),
        "degree": normalize_degree(best.get("degree", "")),
        "field":  best.get("field_of_study", ""),
    }


def activity_score(last_active_str: str | None) -> float:
    """
    Derive activity score [0, 1] from last_active_date.
    0 days ago → 1.0 | 365+ days ago → 0.0  (linear decay)
    """
    if not last_active_str:
        return 0.0
    try:
        last = datetime.strptime(last_active_str, "%Y-%m-%d").date()
        days_ago = max(0, (REFERENCE_DATE - last).days)
        return round(max(0.0, 1.0 - days_ago / 365.0), 4)
    except ValueError:
        return 0.0


def build_career_text(career: list[dict]) -> str:
    """
    Concatenate title + description for every job role.
    Used by TF-IDF ranker and (Phase 5) credibility engine.
    """
    parts = []
    for job in career:
        title = job.get("title", "")
        desc = job.get("description", "")
        if title or desc:
            parts.append(f"{title} {desc}".strip())
    return " ".join(parts)


def build_raw_text(
    current_title: str,
    summary: str,
    career_text: str,
    skill_names: str,
    country: str,
    education_text: str
) -> str:
    """
    Concatenates labeled fields into a single embedding input.
    Provides structured cues for TF-IDF and dense embeddings.
    """
    parts = []
    if current_title:
        parts.append(f"Title: {current_title}")
    if country:
        parts.append(f"Country: {country}")
    if education_text:
        parts.append(f"Education: {education_text}")
    if skill_names:
        parts.append(f"Skills: {skill_names}")
    if summary:
        parts.append(summary)
    if career_text:
        parts.append(career_text)
        
    return " | ".join(p for p in parts if p).strip()


# ---------------------------------------------------------------------------
# Per-candidate feature extraction
# ---------------------------------------------------------------------------

def extract_row(c: dict) -> dict:
    profile  = c.get("profile", {})
    signals  = c.get("redrob_signals", {})
    edu_list = c.get("education", [])
    skills   = c.get("skills", [])
    career   = c.get("career_history", [])

    edu = best_education(edu_list)
    # Improvement 3: Combine degree and field into a single clean string
    education_text = f"{edu['degree']} {edu['field']}".strip()

    # Skills — keep full JSON for credibility engine, also a fast-lookup comma string
    skill_names = ", ".join(s.get("name", "") for s in skills if s.get("name"))

    # Salary — swap if min > max (observed in real data)
    salary_raw = signals.get("expected_salary_range_inr_lpa") or {}
    s_min = safe_float(salary_raw.get("min"), 0.0)
    s_max = safe_float(salary_raw.get("max"), 0.0)
    if s_min > s_max and s_max > 0:
        s_min, s_max = s_max, s_min

    current_title = profile.get("current_title", "")
    summary_text  = profile.get("summary", "")
    c_text        = build_career_text(career)
    country       = profile.get("country", "")

    return {
        # ── Identity ──────────────────────────────────────────────────────
        "candidate_id":              c.get("candidate_id", ""),
        # ── Profile ───────────────────────────────────────────────────────
        "years_exp":                 safe_float(profile.get("years_of_experience"), 0.0),
        "current_title":             current_title,
        "location":                  profile.get("location", ""),
        "country":                   country,
        # ── Skills ────────────────────────────────────────────────────────
        "skills":                    json.dumps(skills),       # full JSON — for credibility engine
        "skills_count":              len(skills),
        # ── Education ─────────────────────────────────────────────────────
        "education_tier":            edu["tier"],
        "highest_degree":            edu["degree"],
        "education_field":           edu["field"],
        "education_text":            education_text,
        # ── Text fields (separate + combined) ─────────────────────────────
        "summary":                   summary_text,             # kept separate for Phase 5
        "career_text":               c_text,                   # title+desc of every job
        "raw_text":                  build_raw_text(current_title, summary_text, c_text, skill_names, country, education_text),
        # ── Behavioral signals ────────────────────────────────────────────
        "response_rate":             safe_float(signals.get("recruiter_response_rate"), 0.0),
        "activity_score":            activity_score(signals.get("last_active_date")),
        "recruiter_saves":           safe_int(signals.get("saved_by_recruiters_30d"), 0),
        "interview_completion_rate": safe_float(signals.get("interview_completion_rate"), 0.0),
        # ── Salary ────────────────────────────────────────────────────────
        "salary_min":                s_min,
        "salary_max":                s_max,
        # ── Auxiliary (used by later phases) ──────────────────────────────
        "notice_period_days":        safe_int(signals.get("notice_period_days"), 30),
        "profile_completeness":      safe_float(signals.get("profile_completeness_score"), 0.0),
        "github_score":              safe_float(signals.get("github_activity_score"), -1.0),
        "open_to_work":              bool(signals.get("open_to_work_flag", False)),
        "willing_to_relocate":       bool(signals.get("willing_to_relocate", False)),
        "preferred_work_mode":       signals.get("preferred_work_mode", "flexible"),
        "num_jobs":                  len(career),
    }


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_feature_store(
    jsonl_path: Path,
    output_path: Path,
    limit: int | None = None,
) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    errors: list[tuple[int, str]] = []

    print(f"\n[INPUT]  {jsonl_path}")
    print(f"[OUTPUT] {output_path}")
    if limit:
        print(f"[LIMIT]  {limit} records (test mode)\n")
    else:
        print()

    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, desc="Parsing", unit="rec")):
            if limit and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(extract_row(json.loads(line)))
            except Exception as exc:
                errors.append((i + 1, str(exc)))

    if errors:
        print(f"\n[WARN] {len(errors)} parse errors -- first 5:")
        for ln, msg in errors[:5]:
            print(f"   Line {ln}: {msg}")

    df = pd.DataFrame(rows)

    # Enforce numeric types
    for col in ["years_exp", "salary_min", "salary_max",
                "response_rate", "activity_score",
                "interview_completion_rate", "profile_completeness", "github_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df.to_parquet(output_path, index=False, engine="pyarrow")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n[DONE] Saved {len(df):,} rows x {len(df.columns)} cols  ({size_mb:.1f} MB)")
    print(f"       Path: {output_path}")
    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build candidate_features.parquet from candidates.jsonl"
    )
    ap.add_argument("--input",  type=Path, default=DEFAULT_JSONL)
    ap.add_argument("--output", type=Path, default=OUTPUT_PARQUET)
    ap.add_argument("--limit",  type=int,  default=None,
                    help="Process only first N records (for quick testing)")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"\n❌  File not found: {args.input}")
        print(
            f"    Copy candidates.jsonl into {DATA_DIR}\n"
            "    e.g.:\n"
            f"      copy \"{DEFAULT_JSONL}\" \"{DATA_DIR / 'candidates.jsonl'}\""
        )
        raise SystemExit(1)

    df = build_feature_store(args.input, args.output, limit=args.limit)

    # ── Quick sanity report ────────────────────────────────────────────────
    print("\n--- Null rates ---")
    for col in ["years_exp", "location", "summary", "response_rate", "career_text"]:
        pct = df[col].isna().mean() * 100 if col in df else -1
        if col == "career_text":
            pct = (df[col] == "").mean() * 100
        print(f"  {col:<32} {pct:.1f}%")

    print(f"\n--- Stats ---")
    print(f"  Experience  : {df['years_exp'].min():.1f} - {df['years_exp'].max():.1f} yrs  (mean {df['years_exp'].mean():.1f})")
    print(f"  Skills count: {df['skills_count'].min()} - {df['skills_count'].max()}  (mean {df['skills_count'].mean():.1f})")
    print(f"  Edu tiers   : {df['education_tier'].value_counts().to_dict()}")
    print(f"  Open to work: {df['open_to_work'].sum():,} ({df['open_to_work'].mean()*100:.0f}%)")
    print(f"  Countries   : {df['country'].value_counts().head(5).to_dict()}")


if __name__ == "__main__":
    main()