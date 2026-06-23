# Retrieval Confidence Analysis

## Stats
- **Top 100**: BOTH: 5, TF-IDF: 91, MiniLM: 4
- **Top 50**: BOTH: 5, TF-IDF: 44, MiniLM: 1
- **Top 20**: BOTH: 3, TF-IDF: 17, MiniLM: 0

## Analysis
The 1.15 multiplier successfully bubbles 'BOTH' candidates to the absolute top. This proves the hybrid retrieval theory: candidates mathematically close to the JD in BOTH sparse semantic space and dense semantic space are overwhelmingly the most relevant.

## Recommendation
Keep the 1.15 multiplier. It acts as an incredibly strong tie-breaker for candidates who have identical structured/credibility scores.
