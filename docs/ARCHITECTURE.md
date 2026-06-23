# Architecture

## 1. System Overview
* High-level goal (Recruiter Showcase, Production ranking engine)
* End-to-end pipeline summary
* Key design principles

## 2. Core Components
* **FastAPI Backend (`api/`)**
  * Routing and entry points
* **Ranking Pipeline (`scout/pipeline/`)**
  * JD Parsing
  * Retrieval (Live Ranker)
  * Structured Scoring
  * Credibility Engine
  * Reasoning Support
* **Frontend (`frontend/`)**
  * Next.js application structure
* **Validation & Testing (`tests/`)**
  * Phase 7 Validation

## 3. Data Flow
* Job Description ingestion
* Feature Generation & Embeddings
* Scoring & Ranking
* Final Output

## 4. Deployment & Infrastructure
* Local setup
* Environment constraints

## 5. Future Evolution
* Planned improvements
