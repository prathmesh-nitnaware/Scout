import json
from pathlib import Path

# Repo-relative paths
ROOT = Path(__file__).resolve().parents[2]
FLAGS_PATH = ROOT / "artifacts" / "validation_flags.json"
JSONL_PATH = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "candidates.jsonl"

def main():
    with open(FLAGS_PATH, "r", encoding="utf-8") as f:
        flags = json.load(f)
        
    exp_cids = [cid for cid, f in flags.items() if any("implausible" in r.lower() for r in f.get("honeypot_reasons", []))]
    print(f"Total flagged by exp-vs-grad rule: {len(exp_cids)}")
    
    # Load data for these 5
    records = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c["candidate_id"] in exp_cids:
                records.append(c)
                
    for c in records:
        cid = c["candidate_id"]
        yoe = float(c.get("profile", {}).get("years_of_experience") or 0)
        edu = [(e.get("degree"), e.get("start_year"), e.get("end_year")) for e in c.get("education", [])]
        career_starts = [job.get("start_date")[:4] for job in c.get("career_history", []) if job.get("start_date")]
        reason = [r for r in flags[cid]["honeypot_reasons"] if "implausible" in r.lower()][0]
        
        print(f"\n{cid}:")
        print(f"  Claimed YOE : {yoe}")
        print(f"  Edu         : {edu}")
        print(f"  Career starts: {career_starts}")
        print(f"  Reason      : {reason}")

if __name__ == "__main__":
    main()
