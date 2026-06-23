# Scout Core Package

This is the primary Python package powering the Scout ranking platform. 

It houses the full deterministic pipeline:
- **Feature Construction**: Scripts for building embeddings and feature parquets.
- **Retrieval Engine**: TF-IDF and MiniLM hybrid candidate sourcing.
- **Scoring Engine**: `structured_scorer.py` applies deterministic weights across Experience, Skills, Career, Education, and Location.
- **Credibility Engine**: `credibility_engine.py` applies strict mathematical penalties for skill inflation, narrative contradiction, and keyword stuffing.
- **Final Orchestration**: `final_ranker.py` and `reasoning.py` combine the models and generate recruiter-friendly summaries.
