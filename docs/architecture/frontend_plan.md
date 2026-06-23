# Frontend Implementation Plan

## Goal
Build a modern, highly responsive Next.js frontend to showcase the Scout ranking engine. The UI must instantly convey the problem, the architecture, and the results to judges within 60 seconds.

## Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Components**: shadcn/ui (Radix UI)
- **Backend Integration**: FastAPI via REST endpoints

## Phase 1: Setup and Initialization
1. Initialize Next.js app in `/frontend`.
2. Install TailwindCSS and configure `shadcn/ui`.
3. Set up the Python FastAPI backend in `/api` to serve as the bridge to the frozen Scout pipeline artifacts.

## Phase 2: FastAPI Backend
1. Create `api/main.py`.
2. Implement `/health` (status check).
3. Implement `/metrics` (returns Pipeline Reduction Summary and Top 100 Title Distribution from artifacts).
4. Implement `/rank` (mock triggering the pipeline, returns `submission_final.csv` contents).
5. Implement `/candidate/{id}` (returns candidate feature data + credibility + reasoning).

## Phase 3: Next.js Frontend Pages
1. **Landing Page (`/`)**: Hero section, architecture diagram visualization, problem statement, call-to-action to rank.
2. **Rank Candidates Page (`/rank`)**: Input field for JD (mock), "Run Pipeline" button, simulated loading states for each phase, and the final Top 100 data table.
3. **Candidate Details Page (`/candidate/[id]`)**: Full breakdown of the candidate's parsed JSONL data versus their structured score, credibility score, and reasoning.
4. **Architecture Page (`/architecture`)**: Visual flow of the 5 phases.
5. **About Page (`/about`)**: Explanation of the MiniLM semantic washout discovery and anti-fraud strategy.

## Phase 4: Polish
- Implement dark mode using Tailwind.
- Add micro-animations (Framer Motion) for the ranking loading states.
- Ensure 100% responsiveness on desktop and tablet (judging formats).
