import sys, json, pandas as pd
sys.path.append('d:/Scout')
from scout.pipeline.structured_scorer import calculate_structured_score
from scout.pipeline.credibility_engine import compute_credibility
from scout.pipeline.final_ranker import get_union_pool, domain_relevance_score

df = pd.read_parquet('artifacts/candidate_features.parquet', engine='pyarrow')
cand = df[df['candidate_id'] == 'CAND_0005260'].iloc[0].to_dict()

with open('artifacts/jd_profile_structured.json', 'r') as f:
    jd = json.load(f)

struct = calculate_structured_score(cand, jd)
cred = compute_credibility(cand, jd)
dr = domain_relevance_score(cand)

print(f"Title: {cand['current_title']}")
print(f"Experience: {cand['years_exp']}")
print("BREAKDOWN:", struct['breakdown'])
print(f"STRUCTURED: {struct['final_score']}")
print(f"CRED: {cred['credibility_score']}")
print(f"DOMAIN RELEVANCE: {dr}")
