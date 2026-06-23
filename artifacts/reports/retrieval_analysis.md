# Retrieval Quality Analysis: TF-IDF vs MiniLM

## Overall Assessment
**MiniLM (Dense Retrieval) performed significantly worse than TF-IDF (Sparse Retrieval) on the raw Job Description.** 
The overlap between the Top 100 of TF-IDF and MiniLM is **0%**.

### TF-IDF Top 20 Analysis
- **Roles Retrieved**: 100% highly relevant titles (`Senior Software Engineer (ML)`, `Computer Vision Engineer`, `AI Research Engineer`, `ML Engineer`, `Data Scientist`).
- **Years of Experience**: Ranged from 2.1 to 8.0 years, generally well-aligned with the JD's 5-9 year requirement.
- **Why it worked**: TF-IDF heavily penalizes common words (like "company", "team", "engineer") and heavily weights rare, highly specific terms ("Transformers", "LoRA", "PyTorch", "LLM"). Candidates who naturally possess these terms in their work history spike to the top.

### MiniLM Top 20 Analysis
- **Roles Retrieved**: 0% relevant titles. The Top 20 consists exclusively of `Mechanical Engineer`, `Civil Engineer`, and `HR Manager`.
- **Why it failed**: `all-MiniLM-L6-v2` is a 384-dimensional dense embedding model with a 256-token limit. The raw Job Description is over 1,500 words of generic corporate boilerplate ("Series A AI-native...", "Let's be honest about this role...", "flexible cadence"). The dense vector gets completely dominated by the generic corporate tone and length of the text. The highly specific technical signal (e.g., "QLoRA") is semantically lost. Thus, it retrieves candidates with similarly generic, long-winded corporate summaries (HR Managers, generic engineers) rather than matching the exact technical stack.

## Questions Answered

**1. Does MiniLM appear better than TF-IDF?**
No. It failed completely. TF-IDF provided highly relevant candidates, whereas MiniLM provided completely irrelevant candidates due to semantic washout.

**2. What candidate patterns improved?**
None under MiniLM. However, TF-IDF showed that sparse keyword matching remains extremely robust for highly technical, jargon-heavy roles.

**3. What candidate patterns remain problematic?**
- **MiniLM Problem**: Dense embeddings cannot handle long, multi-faceted documents like JDs without getting lost in the "average" semantic meaning.
- **TF-IDF Problem**: While the top 20 are generally ML Engineers, TF-IDF is highly susceptible to keyword stuffing. A Data Engineer who arbitrarily lists "LoRA" and "LLM" in their skills array will get a massive artificial boost because those terms have high IDF weights.

**4. Does semantic retrieval reduce keyword-stuffing effects?**
Yes, MiniLM completely ignored keyword stuffing (it completely ignored the keywords!). However, the cost was total loss of relevance. To actually solve keyword stuffing while maintaining relevance, we need Phase 4: Structured Scoring (extracting exactly *where* the skill was used, and weighting career history over a raw skills array), rather than relying on a monolithic dense embedding.
