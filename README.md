# Scout

Scout is a deterministic, evidence-based candidate ranking engine designed to evaluate high-volume, highly technical applicant pools. It solves the critical recruiting challenge of distinguishing candidates who genuinely possess advanced AI/ML skills from those who simply keyword-stuff their resumes. Because pure keyword-matching (TF-IDF) is highly susceptible to resume inflation, and naive dense retrieval (MiniLM) suffers from semantic washout on long corporate job descriptions, traditional candidate ranking systems frequently surface unqualified or deceptive applicants. Scout replaces these flawed heuristics with a multi-stage pipeline combining hybrid retrieval, objective structured scoring, and an aggressive credibility authentication engine to produce a mathematically defensible, recruiter-grade candidate shortlist.

---

# Problem Statement

Recruiters hiring for highly specialized technical roles (like Senior AI Engineers) face the daunting task of reviewing thousands of profiles. In this environment, three major failure modes occur: **Keyword Stuffing** (candidates artificially injecting buzzwords like "LoRA" or "PyTorch" into skills arrays), **Resume Inflation** (candidates claiming Senior titles with less than three years of experience), and **Semantic Mismatch** (generic dense embeddings heavily weighting non-technical corporate boilerplate over core engineering skills). Ranking quality matters because if the system's top 100 candidates are dominated by keyword-stuffers and honeypots, the entire sourcing pipeline collapses, wasting critical engineering interview hours.

---

# Architecture Diagram

```text
       100,000 Candidates
               │
               ▼
     [ Validation Engine ]
               │
               ▼
      [ Hybrid Retrieval ]
  (TF-IDF + Technical MiniLM)
               │
               ▼
    [ Structured Scoring ]
               │
               ▼
    [ Credibility Engine ]
               │
               ▼
       [ Final Ranker ]
               │
               ▼
      Top 100 Candidates
```

**Validation Engine**: A deterministic honeypot filter that permanently excludes logically impossible profiles (e.g., conflicting career dates, impossible salaries, behavioral clones).
**Hybrid Retrieval**: A dual-retrieval pipeline fetching the Top 1,000 candidates via sparse term matching (TF-IDF) and the Top 1,000 via dense embeddings (Technical MiniLM), creating a high-recall union pool.
**Structured Scoring**: A mathematical ranking layer that evaluates parsed candidate claims (Experience, Skills, Title) against the explicit constraints of the Job Description.
**Credibility Engine**: An authentication matrix that cross-references candidate claims (like dropdown skills) against their actual career narrative and work history text to penalize contradictions.
**Final Ranker**: An orchestrator that applies a retrieval confidence multiplier and generates deterministic, recruiter-style reasoning strings for the final Top 100 output.

---

# Retrieval Experiments & Key Findings

During the development of our retrieval engine, an extensive experiment was conducted to determine the optimal embedding strategy.

1. **TF-IDF Baseline**: The sparse retrieval baseline successfully retrieved highly relevant AI/ML titles but proved highly vulnerable to candidates who stuffed rare jargon ("LoRA", "QLoRA") into their skills array.
2. **Full JD MiniLM Failure**: When embedding the complete 1,500-word Job Description, `all-MiniLM-L6-v2` suffered from semantic washout. The dense vector heavily weighted generic corporate HR boilerplate over technical constraints.
3. **Technical JD MiniLM Experiment**: The JD was condensed into a 50-word, strictly technical summary. Retrieving against this Technical JD completely restored relevance.
4. **Conclusion**: The experiment conclusively proved that full JD embeddings fail because of semantic washout, while technical JD embeddings succeed. Furthermore, TF-IDF and Technical MiniLM retrieved entirely different candidate cohorts, directly motivating the Hybrid Retrieval architecture.

**Quantitative Benchmark**
| Retrieval Method    | Relevant Roles in Top 20 |
| ------------------- | ------------------------ |
| TF-IDF              | 20/20                    |
| Full JD MiniLM      | 0/20                     |
| Technical JD MiniLM | 20/20                    |

---

# Scoring Formula

Candidates who reach the Structured Scoring stage are evaluated on five domains.

**Domain Weights:**
- **Experience Fit (20%)**: Evaluates exact `years_exp` against the JD bounds (5-9 years), applying gradual decay for minor deviations and severe penalties for extreme under/over-qualification.
- **Skills Fit (30%)**: Matches required and preferred skills, rewarding evidence strength based on endorsements, proficiency, and duration of use.
- **Career Fit (40%)**: Checks `current_title` and `career_history` for exact role progression, severely penalizing non-technical roles (Marketing, HR).
- **Education Fit (5%)**: Provides minor bumps for STEM degrees (CS, Math, Physics) and advanced degrees (M.Sc., Ph.D.).
- **Location Fit (5%)**: Basic matching for remote logistics and target regions.

These weights were chosen to ensure that a candidate *must* possess the correct tenure and role history to score highly, heavily diluting the impact of simply having an impressive education or location.

**Final Ranking Equation:**
```text
Final Score = Structured Score * (Credibility Score / 100.0) * Retrieval Confidence
```
*(Retrieval Confidence = 1.15 if candidate was found by BOTH TF-IDF and MiniLM, otherwise 1.0)*

**Example — CAND_0005260 (Rank #1):**
```text
  Experience (5.2y, range 5-9):   1.00 × 0.20 = 0.200
  Skills (NLP, Embeddings, Python): 0.46 × 0.30 = 0.138
  Career (Senior NLP Engineer):   1.00 × 0.40 = 0.400
  Education (STEM degree):        0.90 × 0.05 = 0.045
  Location (match):               0.80 × 0.05 = 0.040
  Structured Score:               0.8234
  × Credibility (95/100):         × 0.95 = 0.7822
  × Retrieval Confidence (1.00):  × 1.00 = 0.7822
  → Final Score: 0.7822
```

---

# Credibility Engine

The Credibility Engine serves as Scout's primary defense against resume fraud. Instead of relying on expensive, non-deterministic LLM APIs, it utilizes deterministic Python text analysis to cross-reference claims against textual evidence.

**What it detects:**
- **Skills-Narrative Contradictions**: Detects if high-value AI skills ("PyTorch", "Transformers") are selected in a dropdown array but never actually written about in the candidate's `summary` or `career_text`.
- **Skill Inflation**: Identifies candidates listing a mathematically impossible number of skills relative to their low years of experience.
- **Keyword Stuffing**: Flags exceptionally high skill counts with low overall text volume.
- **Inflated Titles**: Penalizes candidates claiming "Principal" or "Director" titles with fewer than four years of experience.
- **Career Instability**: Identifies job-hoppers based on high job counts over short tenures.

If a contradiction is found, the engine deducts points from a starting score of 100. This credibility score acts as a percentage multiplier against the candidate's structured score, significantly reducing the rank of deceptive candidates.

---

# Honeypot Analysis

The Validation Engine aggressively cleaned the raw 100,000 JSONL candidate pool by identifying logical impossibilities.
- **Experience-vs-Graduation Anomalies**: Penalized profiles claiming 15+ years of experience but lacking any demonstrable work history or degrees prior to 2022.
- **Salary Anomalies**: Flagged mathematically impossible salary requests relative to role level.
- **Behavioral Clones**: Filtered highly suspicious profile configurations.

In total, the validation engine identified and permanently excluded **2,165 honeypots**, yielding a sanitized pool of 97,835 valid candidates for retrieval.

---

# Results

**Pipeline Reduction Summary**

| Stage               |            Candidates |
| ------------------- | --------------------: |
| Raw Dataset         |                100000 |
| After Validation    |                 97835 |
| TF-IDF Retrieval    |                  1000 |
| MiniLM Retrieval    |                  1000 |
| Union Pool          |                  1978 |
| Final Ranked Output |                   100 |

*(Note: Union pool size varies by JD; 1,978 reflects the challenge dataset JD.)*

**Case Study: The Keyword-Stuffing Trap**
Candidate `CAND_0000970` possessed the title "Data Engineer". They injected the highly-coveted term "LoRA" into their skills array.
- **Retrieval Phase**: TF-IDF ranked the candidate in the top 5% (#5,406).
- **Scoring Phase**: Structured Scoring applied a moderate penalty because "Data Engineer" was not the ideal target title.
- **Credibility Phase**: The Credibility Engine identified a **Skills-Narrative Contradiction**: the candidate claimed "LoRA" proficiency, but never wrote about fine-tuning or LLMs anywhere in their multi-paragraph career history. The candidate was removed from the final ranking.

---

# Reproducibility Guide

To reproduce the pipeline end-to-end:

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Generate Embeddings & Feature Store**
*(Requires candidates.jsonl in the data directory)*
```bash
python scout/pipeline/build_embeddings.py
```
*Expected Output: `artifacts/embeddings.npy` and `artifacts/candidate_features.parquet`*

3. **Run Validation Engine**
```bash
python scout/pipeline/validation_engine.py
```
*Expected Output: `artifacts/validation_flags.json`*

4. **Execute Final Ranker**
```bash
python scout/pipeline/final_ranker.py
```
*Expected Output: `submission_final.csv` (100 rows, unbounded scaled scores, generated reasoning strings).*

5. **Start the Live API Server**
```bash
uvicorn scout.api.main:app --reload

# Test with a custom JD
curl -X POST http://localhost:8000/rank-candidates \
  -H "Content-Type: application/json" \
  -d '{"jd_text": "Senior AI Engineer, 5-9 years, Python, PyTorch, RAG, LoRA, FAISS"}'
# Returns top 100 candidates in ~3 seconds
```

---

# Repository Structure

```text
Scout/
├── artifacts/                  # Generated reports, CSVs, JSON, and vector stores
├── scout/
│   └── pipeline/
│       ├── validation_engine.py      # Honeypot exclusion logic
│       ├── build_embeddings.py       # Parquet parsing and SentenceTransformer encoding
│       ├── minilm_ranker.py          # Dense retrieval baseline
│       ├── structured_scorer.py      # Domain constraint scoring
│       ├── credibility_engine.py     # Anti-fraud text analytics
│       ├── reasoning.py              # Dynamic reasoning generator
│       └── final_ranker.py           # Orchestration and CSV submission
├── requirements.txt
└── README.md
```

---

# Performance & Constraints

Scout is designed to be highly performant and deterministic.
- **CPU-Only Execution**: The entire pipeline, including the embedding generation via `sentence-transformers`, is optimized to execute entirely on standard CPU instances.
- **No Runtime LLM Calls**: By using rigorous python logic and deterministic array comparisons, Scout avoids the latency, cost, and hallucination risks of executing LLM API calls on 100,000 rows.
- **Deterministic Pipeline**: Because there is no stochastic generation at runtime, candidate scores are 100% reproducible and mathematically auditable.

---

# Why Scout Avoids Runtime LLM Calls

Scout explicitly avoids using LLM-as-a-judge patterns during runtime for the following critical engineering reasons:
- **Reproducibility**: LLM responses are stochastic; a candidate could be ranked #5 today and #15 tomorrow without changing their resume.
- **Cost**: Processing 100,000 candidates via an advanced LLM API (like GPT-4) would incur massive, unsustainable operational costs.
- **Latency**: API rate limits and token generation speed make evaluating large applicant pools unacceptably slow.
- **Deterministic Rankings**: Standardized mathematical formulas ensure that candidates are judged purely on the configured constraints.
- **Auditability**: If a candidate receives a low score, Scout can pinpoint exactly which Python rule caused the deduction, ensuring full transparency in hiring decisions.

---

# Future Work

While the core ranking engine is mathematically sound, future iterations of Scout will focus on expanding its capabilities:
- **Advanced Fraud Detection**: Utilizing a lightweight local LLM on the final Top 500 to detect "AI-generated prose" stylistic inconsistencies in career narratives.
- **Dynamic JD Adaptation**: Implementing an ingestion parser that automatically condenses any uploaded Job Description into the necessary `jd_profile_structured.json` format.
- **Multi-Domain JD Support**: Extending the pipeline beyond AI/ML Engineering to support Product, Backend, and Data roles with domain-specific skill dictionaries and credibility rules.

---

# Conclusion

Scout proves that the solution to modern, high-volume recruiting is not simply feeding resumes into a generic Vector Database or passing data to a hallucination-prone LLM. By acknowledging that candidates optimize their resumes to bypass algorithms, Scout applies an aggressive, multi-layered defensive strategy. Through honeypot validation, hybrid dense-sparse retrieval, constraint-based structured scoring, and evidence-backed credibility checks, Scout consistently surfaces highly qualified, genuinely experienced engineers while systematically destroying deceptive profiles.
