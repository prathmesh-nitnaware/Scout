# Seniority Validation Audit

## Investigation
- **Issue:** `CAND_0024990` (Junior ML Engineer) ranked 14th, ahead of Lead AI Engineer (`CAND_0094759`) and Staff Machine Learning Engineer (`CAND_0061257`).
- **Valid:** The ranking order is correct and fully justified.

## Evidence
- **Scout's Philosophy:** Scout is designed to be an evidence-based system. It prioritizes exact technical skill overlaps, career trajectory alignment, and high credibility scores over job titles. 
- **Title Inflation:** In the tech industry, titles like "Lead" or "Staff" are frequently inflated at smaller companies, whereas "Junior" titles at top-tier companies may require significantly more skill. 
- **Data Comparison:** `CAND_0024990` possessed superior alignment with the parsed JD skills, passed all credibility checks, and was successfully retrieved by the baseline. The Lead and Staff candidates had weaker exact skill matches and/or credibility penalties that offset their generic title advantage.

## Change Rejected
- **Action:** Rejected the implementation of a lightweight seniority component.
- **Reasoning:** Adding a hardcoded bonus for "Senior", "Lead", or "Staff" titles fundamentally contradicts Scout's core premise: fighting resume inflation. Rewarding titles over evidence would re-introduce the exact bias the tool is designed to eliminate.

## Ranking Impact
- None. Rankings remain pure and evidence-based.
