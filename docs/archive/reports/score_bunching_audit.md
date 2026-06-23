# Score Bunching Audit

## Investigation
- **Issue:** Multiple candidates shared identical scores (e.g., 14 candidates with 0.6213, 10 candidates with 0.6426).
- **Valid:** Yes.
- **Evidence:** Analysis of `submission_final.csv` and `scout/pipeline/final_ranker.py` revealed that candidates meeting the exact same structured criteria (e.g., same experience tier, same skill hit counts) produced identical baseline structured scores. Because the previous tie-breaking mechanism only sorted by `final_score` and `candidate_id`, massive score bunching occurred.

## Change Made
- Modified `final_ranker.py` to implement a deterministic secondary ranking mechanism. 
- The sort order is now: `final_score DESC`, `activity_score DESC` (Behavioral Score), `years_exp DESC`, and `candidate_id ASC`.

## Ranking Impact
- **Before:** Excessive score bunching with arbitrary alphabetical tie-breakers.
- **After:** Ties are broken empirically by behavioral engagement and seniority, ensuring the most active and experienced candidates within a score cluster bubble to the top. The top 20 candidates naturally shifted to favor higher-activity profiles among tied groups.
