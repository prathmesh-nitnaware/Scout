"""Quick data inspection script — run before writing any feature extractors."""
import json
from pathlib import Path

# Repo-relative path to dataset
ROOT = Path(__file__).resolve().parents[2]
JSONL_PATH = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "candidates.jsonl"
SAMPLE_INDICES = {0, 1, 2, 100, 500, 1000, 5000, 10000, 50000, 99000}

samples = []
with open(JSONL_PATH, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i in SAMPLE_INDICES:
            samples.append((i, json.loads(line.strip())))
        if i > 99001:
            break

print(f"Sampled {len(samples)} records\n")

# Check top-level keys
print("=== TOP-LEVEL KEYS ===")
print(list(samples[0][1].keys()))

# Inspect each sample
for line_num, c in samples[:5]:
    cid = c.get("candidate_id", "?")
    profile = c.get("profile", {})
    skills = c.get("skills", [])
    career = c.get("career_history", [])
    edu = c.get("education", [])
    signals = c.get("redrob_signals", {})

    print(f"\n{'='*60}")
    print(f"Record #{line_num}: {cid}")
    print(f"  profile.years_of_experience = {profile.get('years_of_experience')} [{type(profile.get('years_of_experience')).__name__}]")
    print(f"  profile.location            = {profile.get('location')!r}")
    print(f"  profile.current_title       = {profile.get('current_title')!r}")
    print(f"  profile.summary length      = {len(str(profile.get('summary', '')))} chars")
    print(f"  skills count                = {len(skills)}")
    if skills:
        print(f"  skills[0]                   = {skills[0]}")
    print(f"  career_history count        = {len(career)}")
    if career:
        print(f"  career[0].title             = {career[0].get('title')!r}")
        print(f"  career[0].start_date        = {career[0].get('start_date')!r}")
        print(f"  career[0].end_date          = {career[0].get('end_date')!r}")
        print(f"  career[0].description len   = {len(str(career[0].get('description', '')))}")
    print(f"  education count             = {len(edu)}")
    if edu:
        print(f"  edu[0]                      = degree={edu[0].get('degree')!r}, tier={edu[0].get('tier')!r}, field={edu[0].get('field_of_study')!r}")
    print(f"  signals.recruiter_response_rate   = {signals.get('recruiter_response_rate')}")
    print(f"  signals.saved_by_recruiters_30d   = {signals.get('saved_by_recruiters_30d')}")
    print(f"  signals.interview_completion_rate = {signals.get('interview_completion_rate')}")
    print(f"  signals.last_active_date          = {signals.get('last_active_date')!r}")
    print(f"  signals.expected_salary_range_inr_lpa = {signals.get('expected_salary_range_inr_lpa')}")
    print(f"  signals.open_to_work_flag         = {signals.get('open_to_work_flag')}")

# Check null patterns across all 10 samples
print("\n\n=== NULL / MISSING CHECKS ACROSS 10 SAMPLES ===")
fields_to_check = [
    ("profile", "years_of_experience"),
    ("profile", "location"),
    ("profile", "summary"),
    ("redrob_signals", "recruiter_response_rate"),
    ("redrob_signals", "last_active_date"),
    ("redrob_signals", "saved_by_recruiters_30d"),
    ("redrob_signals", "interview_completion_rate"),
    ("redrob_signals", "expected_salary_range_inr_lpa"),
]
for section, field in fields_to_check:
    vals = [c.get(section, {}).get(field) for _, c in samples]
    null_count = sum(1 for v in vals if v is None)
    print(f"  {section}.{field}: {null_count}/{len(samples)} null | sample={vals[:3]}")

print("\n\n=== SKILLS PROFICIENCY VALUES ===")
all_proficiencies = set()
for _, c in samples:
    for s in c.get("skills", []):
        all_proficiencies.add(s.get("proficiency"))
print(f"  Proficiency values: {all_proficiencies}")

print("\n=== EDUCATION TIER VALUES ===")
all_tiers = set()
for _, c in samples:
    for e in c.get("education", []):
        all_tiers.add(e.get("tier"))
print(f"  Tier values: {all_tiers}")

print("\n=== PREFERRED_WORK_MODE VALUES ===")
all_modes = set()
for _, c in samples:
    mode = c.get("redrob_signals", {}).get("preferred_work_mode")
    if mode:
        all_modes.add(mode)
print(f"  Work mode values: {all_modes}")
