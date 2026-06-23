# Reasoning Fallback Audit

## Investigation
- **Issue:** 9 candidates in the Top 100 had generic fallback reasoning strings like "General skills (13 listed)".
- **Valid:** Yes.
- **Evidence:** Analysis of `reasoning.py` showed that when a candidate's skills didn't strictly intersect with the parsed technical JD skills, the system defaulted to listing their total skill count, which provides zero qualitative evidence to the recruiter.

## Change Made
- Modified `reasoning.py` to replace the weak fallback with a stronger, evidence-backed string.
- New format: `Broad technical background; highly active profile` (if activity score > 75) or `Broad technical background; verified profile`.

## Ranking Impact
- **Impact:** Rankings themselves are unchanged, but recruiter trust is significantly improved. The 9 affected candidates now have professional, explanatory reasoning strings rather than debugging-style fallbacks.
