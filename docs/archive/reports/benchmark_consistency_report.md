# Benchmark Consistency Report

## Investigation
- **Issue:** Inconsistent retrieval benchmark numbers reported across different pages (e.g., 20/20 vs 30/30).
- **Valid:** Yes, historically there was confusion between different test runs.
- **Source of Truth:** Traced back to `artifacts/retrieval_analysis.md`, which contains the definitive analysis of the Top 20 retrieval cohort.

## Final Benchmark Numbers
- **TF-IDF:** 20/20 (Vulnerable to keyword stuffing)
- **Full JD MiniLM:** 0/20 (Semantic washout from HR boilerplate)
- **Technical JD MiniLM:** 20/20 (Condensed JD restores relevance)
- **Hybrid (Scout):** 20/20 (Captures distinct, non-overlapping cohorts)

## Change Made
- Audited `README.md`, `frontend/src/app/results/page.tsx`, and `frontend/src/app/architecture/page.tsx`.
- Ensured all sources reflect the strict 20/20 metric derived from the original `retrieval_analysis.md`. The architecture page's 30/30 anomaly has been fully corrected.
