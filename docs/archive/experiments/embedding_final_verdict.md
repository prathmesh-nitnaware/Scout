# Final Embedding Verdict: Full JD vs Technical JD vs TF-IDF

## Overview
We ran a controlled experiment to determine why `all-MiniLM-L6-v2` failed so catastrophically on the initial retrieval pass. We stripped the 1,500-word corporate JD down to a ~50-word strictly technical summary, generated a new embedding, and re-ran the retrieval against the 100K candidates.

## Results

### 1. Did MiniLM fail because of semantic washout from the long JD?
**Yes, absolutely.**
- **Full JD MiniLM** retrieved 0% relevant roles (it surfaced Mechanical Engineers, Civil Engineers, and HR Managers).
- **Technical JD MiniLM** retrieved **100% highly relevant roles** in the Top 10 (`Junior ML Engineer`, `Computer Vision Engineer`, `AI Research Engineer`, `Data Scientist`).
- **Conclusion:** Dense embeddings cannot handle long, generic corporate boilerplate. The technical signal was entirely diluted by the HR language. When we stripped the noise, MiniLM successfully found ML professionals.

### 2. Does Technical-JD MiniLM outperform Full-JD MiniLM?
**Massively.** It completely restored semantic relevance to the targeted domain.

### 3. Is there value in keeping a semantic retrieval signal in Scout?
**Yes, but it solves a different problem than TF-IDF.**
Interestingly, the overlap between Technical MiniLM and TF-IDF in the Top 20 was **0%** (and only 3 in the Top 100).
- **TF-IDF** surfaces candidates who exactly match rare, specific keywords (like "LoRA", "QLoRA", "PyTorch"). 
- **Technical MiniLM** surfaces candidates whose overall profile is deeply saturated with generalized AI/ML semantics, even if they don't perfectly hit the exact rare keywords.
- Both methods found highly relevant candidates, but they found *different* candidates.

### 4. Should Scout use: TF-IDF only, MiniLM only, or a Hybrid?
**Scout should use a TF-IDF + MiniLM Hybrid for Phase 3 Retrieval.**
Because the overlap is near zero, using only one method means we are completely blind to an entire cohort of highly qualified candidates. 
- TF-IDF guarantees we don't miss candidates with exact rare technical skills.
- MiniLM (using the Technical JD) guarantees we don't miss candidates with deep semantic ML experience who may have phrased their skills differently.

### 5. Final Recommendation
**Confidence Level: High**
We should combine the Top 1,000 from TF-IDF and the Top 1,000 from Technical MiniLM into a single unioned candidate pool. This merged pool will then be passed to Phase 4 (Structured Scoring), where the structured engine will meticulously evaluate the context, exact years of experience, and title matches to filter out the keyword-stuffers and semantic mismatches.
