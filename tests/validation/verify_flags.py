"""Verify specific honeypot candidates to ensure flags are correct."""
import json
from pathlib import Path

# Repo-relative dataset and flags
ROOT = Path(__file__).resolve().parents[2]
JSONL = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "candidates.jsonl"
FLAGS = ROOT / "artifacts" / "validation_flags.json"

# Load flags
with open(FLAGS) as f:
    flags = json.load(f)

# Find honeypots by reason type
exp_honeypots = [cid for cid, f in flags.items() if f["is_honeypot"] and any("implausible" in r for r in f["honeypot_reasons"])]
twin_honeypots = [cid for cid, f in flags.items() if f["is_honeypot"] and any("twin" in r for r in f["honeypot_reasons"])]
warnings_only  = [cid for cid, f in flags.items() if not f["is_honeypot"] and f["credibility_warnings"]]

print(f"Exp mismatch honeypots: {len(exp_honeypots)}")
print(f"Twin honeypots: {len(twin_honeypots)}")
print(f"Warnings only (not honeypot): {len(warnings_only)}")

# Check the first 5 exp honeypots against actual data
target_ids = set(exp_honeypots[:5])
found = {}
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        c = json.loads(line.strip())
        cid = c["candidate_id"]
        if cid in target_ids:
            found[cid] = c
        if len(found) >= 5:
            break

print("\n=== VERIFYING EXP MISMATCH HONEYPOTS ===")
for cid in list(target_ids)[:5]:
    c = found.get(cid)
    if not c:
        continue
    yoe = c["profile"]["years_of_experience"]
    edu = c.get("education", [])
    grad_years = [e.get("end_year") for e in edu if e.get("end_year")]
    print(f"\n{cid}:")
    print(f"  Claimed YOE     : {yoe}")
    print(f"  Education       : {[(e.get('degree'), e.get('end_year')) for e in edu]}")
    print(f"  Min grad year   : {min(grad_years) if grad_years else 'N/A'}")
    print(f"  Max possible exp: {2026 - min(grad_years) if grad_years else 'N/A'}")
    print(f"  Flag reason     : {flags[cid]['honeypot_reasons'][0][:100]}")

# Check twin sample
print("\n=== VERIFYING TWIN DETECTION ===")
# Load parquet for twin check
import pandas as pd
df = pd.read_parquet(str(ROOT / "artifacts" / "candidate_features.parquet"),
                     columns=["candidate_id", "response_rate", "activity_score",
                               "recruiter_saves", "interview_completion_rate"])
twin_sample = twin_honeypots[:2]
if twin_sample:
    for cid in twin_sample:
        row = df[df["candidate_id"] == cid]
        if not row.empty:
            r = row.iloc[0]
            print(f"  {cid}: rr={r['response_rate']:.2f} act={r['activity_score']:.2f} saves={r['recruiter_saves']} icr={r['interview_completion_rate']:.2f}")
