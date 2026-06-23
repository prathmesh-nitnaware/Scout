"""
validation_engine.py — Phase 2: Honeypot & Credibility Flag Engine
--------------------------------------------------------------------
Scans all 100K candidates and produces artifacts/validation_flags.json.

Each candidate gets:
    {
        "is_honeypot":          bool,
        "honeypot_reasons":     list[str],   # hard disqualifiers
        "credibility_warnings": list[str],   # soft signals for Phase 5
        "validation_passed":    bool
    }

Honeypot hard rules (credibility = 0.0, excluded from top 100):
    (a) Overlapping employment dates > 6 months
    (b) Claimed experience > years possible since graduation
    (c) Expected salary > 10x computed market rate for their tier
    (d) Behavioral signal vector identical to another candidate (twin)
    (e) Education timelines inverted or set in the future

Soft credibility warnings (used by Phase 5 credibility engine):
    - Salary min > max (inverted range)
    - Very high experience for apparent career start
    - profile_completeness < 30
    - No GitHub + claims software engineering skills

Usage:
    python scout/pipeline/validation_engine.py
    python scout/pipeline/validation_engine.py --limit 5000  # test mode
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT      = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
DATA_DIR  = ROOT / "data"
JSONL_PATH    = DATA_DIR / "candidates.jsonl"
CHALLENGE_DIR = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"
ALT_JSONL     = CHALLENGE_DIR / "candidates.jsonl"
PARQUET_PATH  = ARTIFACTS / "candidate_features.parquet"
FLAGS_OUTPUT  = ARTIFACTS / "validation_flags.json"

REFERENCE_DATE = date(2026, 6, 18)
REFERENCE_YEAR = 2026

# ---------------------------------------------------------------------------
# Market salary bands (INR LPA) by experience bracket
# Used for 10x salary sanity check.
# Market upper bounds are generous — only extreme outliers are flagged.
# ---------------------------------------------------------------------------
MARKET_BANDS: list[tuple[float, float, float]] = [
    # (min_years, max_years, market_max_lpa)
    (0,   2,  15),   # fresher / junior
    (2,   5,  25),   # mid
    (5,   8,  40),   # senior
    (8,  12,  60),   # lead / principal
    (12, 99, 100),   # director+
]

def market_max_lpa(years_exp: float) -> float:
    for ymin, ymax, market_max in MARKET_BANDS:
        if ymin <= years_exp < ymax:
            return market_max
    return 100.0


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def parse_date(s: str | None) -> date | None:
    if s is None:
        return REFERENCE_DATE   # current job — treat end as today
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def overlap_months(s1: date, e1: date, s2: date, e2: date) -> int:
    """Compute overlap in days between two date ranges. 0 if no overlap."""
    overlap_start = max(s1, s2)
    overlap_end   = min(e1, e2)
    if overlap_start >= overlap_end:
        return 0
    return (overlap_end - overlap_start).days


# ---------------------------------------------------------------------------
# Check 1: Employment date overlaps
# ---------------------------------------------------------------------------

def check_date_overlaps(career: list[dict]) -> list[str]:
    """
    Flag if any two jobs overlap by more than 6 months (182 days).
    Returns list of reason strings (empty = no violation).
    """
    reasons: list[str] = []
    jobs = []
    for job in career:
        sd = parse_date(job.get("start_date"))
        ed = parse_date(job.get("end_date"))
        if sd is None:
            continue
        jobs.append((sd, ed or REFERENCE_DATE, job.get("title", "unknown")))

    for i in range(len(jobs)):
        for j in range(i + 1, len(jobs)):
            s1, e1, t1 = jobs[i]
            s2, e2, t2 = jobs[j]
            days = overlap_months(s1, e1, s2, e2)
            if days > 182:
                reasons.append(
                    f"Employment overlap > 6 months: '{t1}' and '{t2}' overlap {days} days"
                )
    return reasons


# ---------------------------------------------------------------------------
# Check 2: Experience vs graduation year plausibility
# ---------------------------------------------------------------------------

def check_experience_plausibility(
    years_exp: float,
    education: list[dict],
    career_history: list[dict],
) -> tuple[list[str], list[str]]:
    """
    Compare claimed years_of_experience against the earliest possible work start.
    Returns (honeypot_reasons, warnings).
    """
    honeypot_reasons: list[str] = []
    warnings: list[str] = []

    grad_years = [
        e.get("end_year")
        for e in education
        if isinstance(e.get("end_year"), int)
    ]
    
    edu_start_years = [
        e.get("start_year")
        for e in education
        if isinstance(e.get("start_year"), int)
    ]

    career_start_years = []
    for job in career_history:
        sd = job.get("start_date", "")
        if sd and len(sd) >= 4:
            try:
                career_start_years.append(int(sd[:4]))
            except ValueError:
                pass

    all_start_signals = career_start_years + edu_start_years
    if grad_years:
        all_start_signals += [min(grad_years)]

    if not all_start_signals:
        return [], []

    earliest_possible_work = min(all_start_signals)
    max_possible_exp = REFERENCE_YEAR - earliest_possible_work

    if years_exp > max_possible_exp + 1:
        honeypot_reasons.append(
            f"Experience implausible: claims {years_exp}yrs but earliest traceable "
            f"work/study year is {earliest_possible_work} "
            f"(max possible {max_possible_exp}yrs as of {REFERENCE_YEAR})"
        )
        
    elif grad_years:
        grad_only_max = REFERENCE_YEAR - min(grad_years)
        if years_exp > grad_only_max + 2:
            warnings.append(
                f"Grad-based experience gap: claims {years_exp}yrs, "
                f"graduated {min(grad_years)} (max {grad_only_max}yrs from grad alone; "
                f"career history starts {earliest_possible_work})"
            )

    return honeypot_reasons, warnings


# ---------------------------------------------------------------------------
# Check 3: Education Sanity (Fix 3)
# ---------------------------------------------------------------------------

def check_education_sanity(education: list[dict]) -> list[str]:
    """
    Flags inverted education timelines and future graduations.
    """
    reasons: list[str] = []
    
    for edu in education:
        start = edu.get("start_year")
        end = edu.get("end_year")
        
        if isinstance(start, int) and isinstance(end, int):
            if start > end:
                reasons.append(f"Education timeline inverted: start year ({start}) > end year ({end}).")
                
        if isinstance(end, int):
            if end > REFERENCE_YEAR:
                reasons.append(f"Future graduation year detected: {end} (Current year: {REFERENCE_YEAR}).")
                
    return reasons


# ---------------------------------------------------------------------------
# Check 4: Salary sanity
# ---------------------------------------------------------------------------

def check_salary_sanity(
    salary_min: float,
    salary_max: float,
    years_exp: float,
) -> tuple[list[str], list[str]]:
    """
    Flag if expected salary exceeds 10x the computed market max for the candidate's tier.
    Also flags inverted salary ranges as a soft warning.
    """
    honeypot_reasons: list[str] = []
    warnings: list[str] = []

    effective_max = max(salary_min, salary_max)
    effective_min = min(salary_min, salary_max)

    market_cap = market_max_lpa(years_exp)
    threshold  = market_cap * 10

    if effective_max > threshold:
        honeypot_reasons.append(
            f"Salary extreme: {effective_max} LPA > 10x market rate ({market_cap} LPA) "
            f"for {years_exp}yrs experience"
        )

    if salary_min > salary_max and salary_max > 0:
        warnings.append(
            f"Salary range inverted: min ({salary_min}) > max ({salary_max})"
        )

    return honeypot_reasons, warnings


# ---------------------------------------------------------------------------
# Check 5: Behavioral twin detection (Fix 1)
# ---------------------------------------------------------------------------

def detect_behavioral_twins(parquet_path: Path) -> set[str]:
    """
    Find candidates with near-identical behavioral signal vectors.
    Uses an 8-factor fingerprint rounded to 3 decimal places to avoid false positives.
    """
    if not parquet_path.exists():
        print("[VALIDATION] Parquet not found — skipping twin detection")
        return set()

    columns_to_load = [
        "candidate_id", "response_rate", "activity_score",
        "recruiter_saves", "interview_completion_rate", 
        "profile_completeness", "github_score",
        "open_to_work", "preferred_work_mode"
    ]
    
    df = pd.read_parquet(parquet_path, engine="pyarrow", columns=columns_to_load)

    # Normalize recruiter_saves to [0, 1] using 95th percentile cap
    saves_max = df["recruiter_saves"].quantile(0.95)
    saves_max = saves_max if saves_max > 0 else 1.0
    df["saves_norm"] = (df["recruiter_saves"] / saves_max).clip(0, 1)

    # Fill NaNs for the fingerprint string concatenation
    df = df.fillna({
        "response_rate": 0.0, "activity_score": 0.0, "interview_completion_rate": 0.0,
        "profile_completeness": 0.0, "github_score": 0.0,
        "open_to_work": False, "preferred_work_mode": "unknown"
    })

    # Build fingerprint: 8 dimensions, tight tolerances (.round(3))
    df["fingerprint"] = (
        df["response_rate"].round(3).astype(str) + "|" +
        df["activity_score"].round(3).astype(str) + "|" +
        df["saves_norm"].round(3).astype(str) + "|" +
        df["interview_completion_rate"].round(3).astype(str) + "|" +
        df["profile_completeness"].round(3).astype(str) + "|" +
        df["github_score"].round(3).astype(str) + "|" +
        df["open_to_work"].astype(str) + "|" +
        df["preferred_work_mode"].astype(str)
    )

    groups = df.groupby("fingerprint")["candidate_id"].apply(list)
    twin_ids: set[str] = set()
    twin_cluster_count = 0
    
    for fp, cids in groups.items():
        if len(cids) > 1:
            twin_cluster_count += 1
            for cid in cids:
                twin_ids.add(cid)

    print(f"[VALIDATION] Twin detection: {len(twin_ids):,} candidates in "
          f"{twin_cluster_count:,} duplicate-fingerprint clusters")
    return twin_ids


# ---------------------------------------------------------------------------
# Additional soft warnings (non-disqualifying)
# ---------------------------------------------------------------------------

def check_soft_signals(candidate: dict) -> list[str]:
    """
    Non-disqualifying credibility warnings for Phase 5.
    """
    warnings: list[str] = []
    profile  = candidate.get("profile", {})
    signals  = candidate.get("redrob_signals", {})
    skills   = candidate.get("skills", [])

    completeness = signals.get("profile_completeness_score", 100)
    if completeness < 30:
        warnings.append(f"Low profile completeness: {completeness:.1f}%")

    yoe = profile.get("years_of_experience", 0)
    skill_count = len(skills)
    if skill_count >= 15 and yoe < 2:
        warnings.append(
            f"High skill count ({skill_count}) with low experience ({yoe}yrs)"
        )

    open_to_work = signals.get("open_to_work_flag", False)
    last_active_str = signals.get("last_active_date")
    if open_to_work and last_active_str:
        try:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
            days_inactive = (REFERENCE_DATE - last_active).days
            if days_inactive > 90:
                warnings.append(
                    f"Open to work but inactive {days_inactive} days"
                )
        except ValueError:
            pass

    return warnings


# ---------------------------------------------------------------------------
# Main validation loop
# ---------------------------------------------------------------------------

def validate_all(
    jsonl_path: Path,
    parquet_path: Path,
    output_path: Path,
    limit: int | None = None,
) -> dict[str, dict]:
    """
    Run all validation checks over all candidates.
    Returns dict of candidate_id -> flag_object.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n[VALIDATION] Pass 1: Scanning JSONL ...")
    flags: dict[str, dict] = {}
    counts = Counter()

    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, desc="Validating", unit="rec")):
            if limit and i >= limit:
                break
            line = line.strip()
            if not line:
                continue

            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue

            cid      = c.get("candidate_id", f"UNK_{i}")
            profile  = c.get("profile", {})
            signals  = c.get("redrob_signals", {})
            career   = c.get("career_history", [])
            edu      = c.get("education", [])

            years_exp   = float(profile.get("years_of_experience") or 0)
            salary_raw  = signals.get("expected_salary_range_inr_lpa") or {}
            salary_min  = float(salary_raw.get("min") or 0)
            salary_max  = float(salary_raw.get("max") or 0)

            honeypot_reasons: list[str] = []
            warnings:         list[str] = []

            # Check (a): Employment date overlaps
            overlap_reasons = check_date_overlaps(career)
            honeypot_reasons.extend(overlap_reasons)
            if overlap_reasons:
                counts["overlap"] += 1

            # Check (b): Experience vs graduation
            exp_h, exp_w = check_experience_plausibility(years_exp, edu, career)
            honeypot_reasons.extend(exp_h)
            warnings.extend(exp_w)
            if exp_h:
                counts["exp_implausible"] += 1
                
            # Check (c): Education sanity
            edu_h = check_education_sanity(edu)
            honeypot_reasons.extend(edu_h)
            if edu_h:
                counts["edu_invalid"] += 1

            # Check (d): Salary sanity
            sal_h, sal_w = check_salary_sanity(salary_min, salary_max, years_exp)
            honeypot_reasons.extend(sal_h)
            warnings.extend(sal_w)
            if sal_h:
                counts["salary_extreme"] += 1
            if sal_w:
                counts["salary_inverted"] += 1

            # Soft warnings
            soft_w = check_soft_signals(c)
            warnings.extend(soft_w)

            is_honeypot = len(honeypot_reasons) > 0
            if is_honeypot:
                counts["honeypot_total"] += 1

            flags[cid] = {
                "is_honeypot":          is_honeypot,
                "honeypot_reasons":     honeypot_reasons,
                "credibility_warnings": warnings,
                "validation_passed":    not is_honeypot,
            }

    print(f"\n[VALIDATION] Pass 1 complete: {len(flags):,} candidates")
    print(f"  Date overlaps > 6mo : {counts['overlap']:,}")
    print(f"  Exp implausible     : {counts['exp_implausible']:,}")
    print(f"  Education invalid   : {counts['edu_invalid']:,}")
    print(f"  Salary extreme (10x): {counts['salary_extreme']:,}")
    print(f"  Salary inverted     : {counts['salary_inverted']:,}")
    print(f"  Honeypots so far    : {counts['honeypot_total']:,}")

    # ── Pass 2: Behavioral twin detection on parquet ─────────────────────────
    print(f"\n[VALIDATION] Pass 2: Behavioral twin detection ...")
    twin_ids = detect_behavioral_twins(parquet_path)

    twin_honeypot_new = 0
    for cid in twin_ids:
        if cid in flags:
            reason = "Behavioral twin: identical signal fingerprint to another candidate"
            if reason not in flags[cid]["honeypot_reasons"]:
                flags[cid]["honeypot_reasons"].append(reason)
                if not flags[cid]["is_honeypot"]:
                    flags[cid]["is_honeypot"]       = True
                    flags[cid]["validation_passed"]  = False
                    counts["honeypot_total"]         += 1
                    twin_honeypot_new                += 1

    counts["behavioral_twins"] = len(twin_ids)
    print(f"  Behavioral twins    : {len(twin_ids):,}  "
          f"({twin_honeypot_new:,} newly flagged as honeypot)")

    # ── Write output ─────────────────────────────────────────────────────────
    total_honeypots = sum(1 for f in flags.values() if f["is_honeypot"])
    total_valid     = len(flags) - total_honeypots

    print(f"\n[VALIDATION] Final counts:")
    print(f"  Total candidates    : {len(flags):,}")
    print(f"  Honeypots (excluded): {total_honeypots:,} ({total_honeypots/len(flags)*100:.2f}%)")
    print(f"  Validation passed   : {total_valid:,}")
    print(f"\n  Breakdown:")
    print(f"    Date overlaps > 6mo : {counts['overlap']:,}")
    print(f"    Exp implausible     : {counts['exp_implausible']:,}")
    print(f"    Education invalid   : {counts['edu_invalid']:,}")
    print(f"    Salary extreme (10x): {counts['salary_extreme']:,}")
    print(f"    Behavioral twins    : {counts['behavioral_twins']:,}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(flags, f, separators=(",", ":"))

    size_kb = output_path.stat().st_size / 1024
    print(f"\n[VALIDATION] Saved: {output_path}  ({size_kb:.0f} KB)")

    return flags


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_flags(flags_path: Path | None = None) -> dict[str, dict]:
    path = flags_path or FLAGS_OUTPUT
    if not path.exists():
        raise FileNotFoundError(
            f"validation_flags.json not found at {path}\n"
            "Run validation_engine.py first."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_valid_candidate(cid: str, flags: dict[str, dict]) -> bool:
    entry = flags.get(cid)
    if entry is None:
        return True
    return entry.get("validation_passed", True)


# ---------------------------------------------------------------------------
# Report helper
# ---------------------------------------------------------------------------

def print_honeypot_report(flags: dict[str, dict]) -> None:
    honeypots = {cid: f for cid, f in flags.items() if f["is_honeypot"]}
    print(f"\n{'='*60}")
    print(f"HONEYPOT REPORT")
    print(f"{'='*60}")
    print(f"Total candidates  : {len(flags):,}")
    print(f"Honeypots detected: {len(honeypots):,} ({len(honeypots)/len(flags)*100:.2f}%)")
    print(f"Valid candidates  : {len(flags)-len(honeypots):,}")
    print()

    reason_counts: Counter = Counter()
    for f in honeypots.values():
        for r in f["honeypot_reasons"]:
            if "overlap" in r.lower():
                reason_counts["Employment date overlap > 6 months"] += 1
            elif "implausible" in r.lower() or "experience" in r.lower():
                reason_counts["Experience vs graduation mismatch"] += 1
            elif "future" in r.lower() or "inverted" in r.lower():
                reason_counts["Invalid education timelines"] += 1
            elif "salary" in r.lower() or "10x" in r.lower():
                reason_counts["Salary > 10x market rate"] += 1
            elif "twin" in r.lower():
                reason_counts["Behavioral twin (duplicate signal fingerprint)"] += 1
            else:
                reason_counts["Other"] += 1

    print("Breakdown by disqualification reason:")
    for reason, count in reason_counts.most_common():
        print(f"  {reason:<50} {count:>6}")

    print(f"\nSample honeypots (first 5):")
    for cid, f in list(honeypots.items())[:5]:
        print(f"  {cid}: {f['honeypot_reasons'][0][:80]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Run validation engine on all candidates")
    ap.add_argument("--jsonl",   type=Path, default=None)
    ap.add_argument("--parquet", type=Path, default=PARQUET_PATH)
    ap.add_argument("--output",  type=Path, default=FLAGS_OUTPUT)
    ap.add_argument("--limit",   type=int,  default=None,
                    help="Process only first N records (test mode)")
    args = ap.parse_args()

    jsonl_path = args.jsonl
    if jsonl_path is None:
        if JSONL_PATH.exists():
            jsonl_path = JSONL_PATH
        elif ALT_JSONL.exists():
            jsonl_path = ALT_JSONL
        else:
            print(f"[ERROR] candidates.jsonl not found in {DATA_DIR} or {CHALLENGE_DIR}")
            raise SystemExit(1)

    flags = validate_all(
        jsonl_path=jsonl_path,
        parquet_path=args.parquet,
        output_path=args.output,
        limit=args.limit,
    )

    print_honeypot_report(flags)


if __name__ == "__main__":
    main()