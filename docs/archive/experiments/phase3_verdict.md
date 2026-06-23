# Phase 3 Verdict

## A. Retrieval Performance
**TF-IDF Wins (Massively).** 

MiniLM completely failed to retrieve relevant roles (producing Mechanical Engineers, HR Managers, and Civil Engineers in the top 20). TF-IDF successfully retrieved highly relevant AI and ML Engineering roles, despite being susceptible to keyword stuffing traps.

## B. Recommendation
**Refine retrieval first, but move to Phase 4.**

We have formally validated that dense retrieval (MiniLM) on long, corporate boilerplate JDs fails because semantic specificity is washed out. Sparse retrieval (TF-IDF) captures the highly technical stack but is blind to keyword context.
To fix this, we should skip MiniLM altogether and use TF-IDF to generate the Top 1,000 candidate pool. From that Top 1,000, we immediately proceed to Phase 4 (Structured Scoring Engine) to re-rank the candidates by evaluating the *context* of those keywords (e.g., verifying experience fits, extracting exactly where PyTorch was used, and checking title alignments).

## C. Confidence Level
**High.** 
We definitively proved why standard vector DB (MiniLM + FAISS) tutorials fail in real-world technical recruiting, avoiding a massive architecture trap. We know exactly what to build next to fix it.

## D. Key Findings
1. **Semantic Washout**: Dense embeddings limit out at 256/512 tokens. Passing an entire JD full of HR boilerplate ("We are a Series A startup...", "Hybrid cadence") completely destroys the embedding's ability to find specific technical skills.
2. **Sparse is King for Tech Stacks**: TF-IDF naturally weights rare terms like "LoRA" and "PyTorch" highly, making it exceptional at finding candidates with the right stack.
3. **The Trap Problem Remains**: TF-IDF can't distinguish a Data Engineer who stuffs "LoRA" in a skills array from an AI Researcher who used "LoRA" in their career history. This proves that Phase 4 (Structured Scoring) is the actual core of the Scout engine, not Phase 3 (Retrieval).
