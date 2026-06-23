# Scout Runtime Feasibility Report

## 1. Module Verification
All required modules exist and execute successfully. The backend is cleanly separated into modular files.

- `jd_parser.py`: Validated.
- `build_embeddings.py`: Validated.
- `minilm_ranker.py`: Validated.
- `structured_scorer.py`: Validated.
- `credibility_engine.py`: Validated.
- `reasoning.py`: Validated.

## 2. Module Analysis

| Module | Inputs | Outputs | Reusable at Runtime? | Approx Runtime |
|--------|--------|---------|----------------------|----------------|
| **jd_parser.py** | Raw JD string | Dict (`required_skills`, `raw_jd`) | **YES** | < 0.1s |
| **build_embeddings.py** | `candidate_features.parquet` | `embeddings.npy` | **NO** (Offline only) | ~Minutes (for 100k) |
| **minilm_ranker.py** | JD string, `embeddings.npy` | Sorted list/CSV of candidates | **YES** (with refactor to return data instead of writing CSV) | ~0.5s (JD encoding + cosine sim) |
| **structured_scorer.py** | Candidate dict, JD dict | Final Score & Breakdown | **YES** | < 0.1s |
| **credibility_engine.py** | Candidate dict | Credibility Score & Flags | **YES** | < 0.1s |
| **reasoning.py** | Candidate dict, Scores, etc. | Explanatory string | **YES** | < 0.1s |

## 3. Live Pipeline Feasibility
**Can a live pipeline be executed WITHOUT recomputing candidate embeddings?**
**YES.** The architecture perfectly supports this. The heavy computation (candidate embeddings) is already done. A live pipeline only needs to embed the single newly provided JD text using `SentenceTransformer` (which takes milliseconds) and run a fast vectorized cosine similarity against the pre-loaded 100K `embeddings.npy`. The union pool is then passed to the fast, deterministic Python functions in Phase 4 & 5.

## 4. Artifact Confirmation
I have inspected the `artifacts/` directory and confirmed the presence of:
- [x] `candidate_features.parquet` (72.1 MB)
- [x] `embeddings.npy` (153.6 MB)
- [x] `technical_jd_embedding.npy` (1.6 KB)
- [x] All other required JSON/CSV artifacts.

## 5. Expected Runtime Estimate
If the API server (e.g., FastAPI) loads `candidate_features.parquet` and `embeddings.npy` into memory on startup (Warm Start):
- **JD Parsing & Embedding:** ~0.5s
- **TF-IDF fit/transform on 100k (if not cached):** ~5.0s - 8.0s
- **Dense Cosine Similarity:** ~0.1s
- **Structured Scoring & Credibility (on ~2,000 Union Pool):** ~0.2s
- **Total Expected Runtime:** **~5 to 10 seconds** per request (can be optimized to <2s if the TF-IDF matrix is also pre-computed and held in RAM).

---

## Verdict
**B) Minor Refactor**

**Reasoning:** The mathematical logic and core processing functions are perfectly sound and ready to go. However, the current scripts (like `final_ranker.py` and `minilm_ranker.py`) are strictly structured as offline batch scripts that read from and write to the disk (e.g., `pd.read_parquet`, `to_csv`). To run this live behind `POST /rank`, we just need a minor refactor to wrap these existing functions into a single in-memory pipeline function that returns JSON rather than saving artifacts.
