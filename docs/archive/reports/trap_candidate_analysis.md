# Trap Candidate Analysis

## Overview
We inspected known trap profiles to see how they moved between TF-IDF (Sparse) and MiniLM (Dense) retrieval.

### Trap 1: Data Engineer Claiming Advanced AI Skills
**Candidate ID:** `CAND_0000970`
**Profile:** Current Title is `Data Engineer`, but skills array contains highly specific AI keywords like `LoRA`.
- **TF-IDF Rank:** 5,406
- **MiniLM Rank:** 97,399
- **Analysis:** TF-IDF was successfully "tricked" into giving this candidate a massive boost (top 5.4%) because "LoRA" is an extremely rare term with a massive IDF weight. MiniLM completely rejected the candidate (bottom 3%) because the semantic meaning of the profile (Data Engineering tasks) did not align with the generic semantic tone of the JD.

### Trap 2: Marketing Manager with Scattered Tech Skills
**Candidate ID:** `CAND_0000004`
**Profile:** Current Title is `Marketing Manager`, but lists skills like `Node.js`, `AI`, and `Machine Learning`.
- **TF-IDF Rank:** 33,878
- **MiniLM Rank:** 55,541
- **Analysis:** TF-IDF ranked them higher due to the explicit keyword overlap ("Machine Learning", "AI"). MiniLM placed them near the median, recognizing that a Marketing Manager's summary semantically diverges from an Engineering JD, but the failure of MiniLM overall means this candidate still beat out tens of thousands of actual engineers.

## Conclusion
- **TF-IDF** is highly susceptible to exact keyword stuffing. A single rare keyword (like `LoRA`) can catapult an irrelevant candidate into the top 5%.
- **MiniLM** ignores keyword stuffing because it fails to capture specific technical keywords entirely. 
- Neither baseline model alone is sufficient to safely filter traps. We must rely on Phase 4 (Structured Scoring) to look at *where* the skills are located (e.g., verifying `LoRA` is in the `career_text` of an `AI Engineer` role, not just dumped in the skills array of a `Data Engineer` role).
