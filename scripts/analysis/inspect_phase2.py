"""Spot-check career dates, salary edge cases, and graduation years across 50 random records."""
import json, random
from pathlib import Path

# Repo-relative path to dataset
ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "candidates.jsonl"

# Sample from different positions in the file
indices = set(random.sample(range(100000), 50))
indices.update({0, 1, 2, 100, 500, 1000, 5000, 10000, 50000, 99000})

samples = []
with open(JSONL, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in indices:
            samples.append((i, json.loads(line.strip())))
        if len(samples) >= 60:
            break

print(f"Sampled {len(samples)} records\n")

# --- Check 1: Date formats in career_history ---
print("=== DATE FORMAT SAMPLES ===")
date_formats_seen = set()
null_end_date_count = 0
for _, c in samples[:20]:
    for job in c.get("career_history", []):
        sd = job.get("start_date")
        ed = job.get("end_date")
        if sd:
            date_formats_seen.add(type(sd).__name__ + ":" + str(sd)[:7])
        if ed is None:
            null_end_date_count += 1
print(f"  start_date types/formats: {list(date_formats_seen)[:5]}")
print(f"  null end_date count (current jobs): {null_end_date_count}")

# --- Check 2: Overlapping dates ---
print("\n=== OVERLAP SCAN (50 records) ===")
overlap_count = 0
from datetime import datetime, date

def parse_date(s):
    if s is None:
        return date(2026, 6, 18)  # treat null (current) as today
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except:
        return None

for _, c in samples:
    cid = c["candidate_id"]
    career = c.get("career_history", [])
    jobs = []
    for job in career:
        sd = parse_date(job.get("start_date"))
        ed = parse_date(job.get("end_date"))
        if sd and ed:
            jobs.append((sd, ed, job.get("title", "")))
    
    # Check pairwise overlaps
    for i in range(len(jobs)):
        for j in range(i+1, len(jobs)):
            s1, e1, t1 = jobs[i]
            s2, e2, t2 = jobs[j]
            overlap_start = max(s1, s2)
            overlap_end = min(e1, e2)
            if overlap_start < overlap_end:
                overlap_days = (overlap_end - overlap_start).days
                if overlap_days > 182:  # > 6 months
                    print(f"  OVERLAP > 6mo: {cid} | {t1} ({s1} to {e1}) overlaps {t2} ({s2} to {e2}) by {overlap_days} days")
                    overlap_count += 1

print(f"  Total overlaps > 6 months in sample: {overlap_count}")

# --- Check 3: Experience vs graduation ---
print("\n=== EXPERIENCE vs GRADUATION YEAR ===")
REF_YEAR = 2026
suspicious = 0
for _, c in samples:
    cid = c["candidate_id"]
    yoe = c.get("profile", {}).get("years_of_experience", 0)
    edu = c.get("education", [])
    if edu:
        # Use earliest graduation end_year
        grad_years = [e.get("end_year") for e in edu if e.get("end_year")]
        if grad_years:
            earliest_grad = min(grad_years)
            max_possible_exp = REF_YEAR - earliest_grad
            if yoe > max_possible_exp + 2:  # +2 year tolerance
                print(f"  SUSPICIOUS: {cid} claims {yoe}yrs exp, graduated {earliest_grad} (max possible ~{max_possible_exp})")
                suspicious += 1
print(f"  Suspicious experience/graduation mismatches: {suspicious}")

# --- Check 4: Salary ranges ---
print("\n=== SALARY RANGE EDGE CASES ===")
for _, c in samples[:30]:
    sal = c.get("redrob_signals", {}).get("expected_salary_range_inr_lpa", {})
    if sal:
        smin = sal.get("min", 0)
        smax = sal.get("max", 0)
        yoe = c.get("profile", {}).get("years_of_experience", 0)
        if smin > smax:
            print(f"  SALARY INVERTED: {c['candidate_id']} min={smin} max={smax}")
        if smax > 200:
            print(f"  SALARY EXTREME: {c['candidate_id']} max={smax} LPA yoe={yoe}")

# --- Check 5: Behavioral signal value ranges ---
print("\n=== BEHAVIORAL SIGNAL RANGES ===")
rr_vals = [c.get("redrob_signals", {}).get("recruiter_response_rate", None) for _, c in samples]
icr_vals = [c.get("redrob_signals", {}).get("interview_completion_rate", None) for _, c in samples]
saves_vals = [c.get("redrob_signals", {}).get("saved_by_recruiters_30d", None) for _, c in samples]
act_vals = [c.get("redrob_signals", {}).get("last_active_date", None) for _, c in samples]

print(f"  response_rate range: {min(v for v in rr_vals if v is not None):.2f} - {max(v for v in rr_vals if v is not None):.2f}")
print(f"  interview_completion_rate range: {min(v for v in icr_vals if v is not None):.2f} - {max(v for v in icr_vals if v is not None):.2f}")
print(f"  saved_by_recruiters_30d range: {min(v for v in saves_vals if v is not None)} - {max(v for v in saves_vals if v is not None)}")
print(f"  last_active_date samples: {[v for v in act_vals[:5]]}")
