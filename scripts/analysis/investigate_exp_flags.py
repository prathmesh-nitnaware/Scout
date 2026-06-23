"""
Investigate 50 random experience-vs-graduation flagged candidates.
Goal: determine if the rule is catching real honeypots or generating false positives.

Key false-positive patterns to look for:
  A) Only highest/latest degree listed (BSc not in data, only MBA 2020)
  B) Candidate worked during studies (internship counted as experience)
  C) Career start_date predates graduation (possible, legit)
  D) education list has multiple entries -- check if min year is the actual earliest

Run: python investigate_exp_flags.py
"""

import json
import random
from datetime import date
from pathlib import Path

# Repo-relative paths
ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "candidates.jsonl"
FLAGS = ROOT / "artifacts" / "validation_flags.json"
REF_YR = 2026

# --- Load flags, isolate exp-vs-graduation honeypots ---
with open(FLAGS, encoding="utf-8") as f:
    all_flags = json.load(f)

exp_flagged = [
    cid for cid, fl in all_flags.items()
    if fl["is_honeypot"] and any("implausible" in r for r in fl["honeypot_reasons"])
]
print(f"Total exp-vs-graduation honeypots: {len(exp_flagged):,}")

# Sample 50 random flagged candidates
sample_ids = set(random.sample(exp_flagged, min(50, len(exp_flagged))))

# Load their raw records from JSONL
records = {}
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        c = json.loads(line.strip())
        cid = c["candidate_id"]
        if cid in sample_ids:
            records[cid] = c
        if len(records) >= 50:
            break

print(f"\nInspecting {len(records)} sampled candidates\n")
print("=" * 90)

# Counters for classification
buckets = {
    "clear_honeypot":    0,  # obviously wrong (no way to have that exp)
    "likely_fp":         0,  # probably a false positive
    "ambiguous":         0,  # unclear
}
fp_notes = []

for cid, c in records.items():
    profile = c.get("profile", {})
    edu     = c.get("education", [])
    career  = c.get("career_history", [])

    yoe         = profile.get("years_of_experience", 0)
    grad_years  = sorted([e.get("end_year") for e in edu if e.get("end_year")])
    start_years = []
    for e in edu:
        sy = e.get("start_year")
        if sy:
            start_years.append(sy)

    # Earliest possible work start: could be during studies
    earliest_grad   = min(grad_years) if grad_years else None
    earliest_start  = min(start_years) if start_years else earliest_grad
    # Career history first job start
    career_starts = []
    for job in career:
        sd = job.get("start_date", "")
        if sd and len(sd) >= 4:
            try:
                career_starts.append(int(sd[:4]))
            except ValueError:
                pass

    earliest_career_year = min(career_starts) if career_starts else None
    max_possible_from_career = (REF_YR - earliest_career_year) if earliest_career_year else None
    max_possible_from_grad   = (REF_YR - earliest_grad) if earliest_grad else None

    # Classify
    gap = yoe - (max_possible_from_grad or 0)

    flag_reason = all_flags[cid]["honeypot_reasons"][0]

    # Is the career history consistent with claimed YOE?
    career_consistent = (
        max_possible_from_career is not None and
        yoe <= max_possible_from_career + 1
    )

    if career_consistent and gap > 2:
        # Career dates support the experience — education data is incomplete
        label = "likely_fp"
        buckets["likely_fp"] += 1
        fp_notes.append(f"{cid}: career says {earliest_career_year}, grad says {earliest_grad}, claims {yoe}yr")
    elif gap > 5:
        label = "clear_honeypot"
        buckets["clear_honeypot"] += 1
    else:
        label = "ambiguous"
        buckets["ambiguous"] += 1

    print(f"{cid} [{label}]")
    print(f"  Claimed YOE      : {yoe} years")
    print(f"  Edu records      : {[(e.get('degree'), e.get('start_year'), e.get('end_year')) for e in edu]}")
    print(f"  Grad years (min) : {earliest_grad}")
    print(f"  Max exp from grad: {max_possible_from_grad}")
    print(f"  Career start yrs : {career_starts}")
    print(f"  Career consistent: {career_consistent} (career max_possible={max_possible_from_career})")
    print(f"  Gap (YOE - possible): {gap:.1f} yrs")
    print(f"  Flag reason      : {flag_reason[:90]}")
    print()

print("=" * 90)
print(f"\nCLASSIFICATION SUMMARY ({len(records)} sampled):")
print(f"  Clear honeypots : {buckets['clear_honeypot']:>3}  ({buckets['clear_honeypot']/len(records)*100:.0f}%)")
print(f"  Likely FP       : {buckets['likely_fp']:>3}  ({buckets['likely_fp']/len(records)*100:.0f}%)")
print(f"  Ambiguous       : {buckets['ambiguous']:>3}  ({buckets['ambiguous']/len(records)*100:.0f}%)")

print(f"\nLIKELY FALSE POSITIVES (career history contradicts flag):")
for note in fp_notes[:10]:
    print(f"  {note}")
