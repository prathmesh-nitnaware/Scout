# Scout Documentation

Welcome to the Scout documentation directory. This folder contains all the architectural blueprints, algorithmic breakdowns, and historical analysis reports detailing how the Scout platform was built and evaluated.

## Directory Structure

### Core System Documents
These files describe the active components of the Scout backend pipeline:
- **`ARCHITECTURE.md`**: High-level overview of the backend ranking pipeline, infrastructure, and design patterns.
- **`SCORING_ENGINE.md`**: Detailed breakdown of the deterministic structured scoring formulas (Experience, Skills, Career, Education, Location).
- **`CREDIBILITY_ENGINE.md`**: Explanation of the fraud-detection mechanisms, including penalty logic for keyword stuffing, title inflation, and narrative contradictions.

### Analysis & Evaluation
These files detail the rigorous testing and experimental results of the pipeline:
- **`BENCHMARK_RESULTS.md`**: Performance metrics and comparison against baseline TF-IDF retrieval methods.
- **`RETRIEVAL_ANALYSIS.md`**: Deep dive into the hybrid retrieval approach combining technical semantic embeddings with keyword matching.

### Subdirectories
- **`architecture/`**: Contains specific technical design plans for individual subsystems (e.g., `frontend_architecture.md`, `frontend_plan.md`).
- **`archive/`**: Contains all historical data, original hackathon/challenge specifications, superseded experiment reports, and debug scripts from the development phase. This folder serves as a historical record of the pipeline's evolution.
