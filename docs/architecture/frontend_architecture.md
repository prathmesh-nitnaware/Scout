# Frontend Architecture

## High-Level Topology
```text
[ Client (Browser) ]
        │
    (REST HTTP)
        │
[ Next.js 15 Server (App Router) ]
        │
    (REST HTTP)
        │
[ FastAPI Backend ]
        │
   (File System)
        │
[ Scout Artifacts & CSVs ]
```

## Data Flow
Because the Python backend ranking engine is frozen, the FastAPI server acts as a Read-Only API layer on top of the generated artifacts (`submission_final.csv`, `candidate_features.parquet`, etc.). 
- When the user clicks "Run Ranking" on the frontend, the UI simulates the 5 phases with a loading sequence, then requests the final JSON payload from the FastAPI `/rank` endpoint.
- FastAPI reads the static CSV and Parquet files, joining them to return a comprehensive JSON list to Next.js.
- Next.js renders the Data Table.

## Directory Structure
```text
Scout/
├── api/
│   ├── main.py
│   ├── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── rank/
│   │   │   ├── candidate/[id]/
│   │   │   ├── architecture/
│   │   │   └── about/
│   │   ├── components/
│   │   │   ├── ui/ (shadcn)
│   │   │   ├── CandidateTable.tsx
│   │   │   ├── MetricCard.tsx
│   │   │   └── Navbar.tsx
│   │   └── lib/
│   │       └── api.ts
```
