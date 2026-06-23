# Scout Frontend Dashboard

This is the Next.js frontend application for **Scout**, a recruiter-facing dashboard designed to interface with the Scout Candidate Ranking API. It provides a visual interface for recruiters to rank, analyze, and deep-dive into AI/ML candidate profiles.

## Features

- **Live Ranking Interface (`/rank`)**: Submit a Job Description (JD) to the backend API and retrieve ranked candidate results in real-time.
- **Results Dashboard (`/results`)**: View top candidates, their structured scores, credibility flags, and reasoning.
- **Candidate Deep Dive (`/candidate/[id]`)**: Explore detailed structural breakdowns, skill matches, and career timeline for individual candidates.
- **System Architecture (`/architecture`)**: Documentation of the frontend and backend technical architecture.
- **Case Study (`/case-study`)**: Detailed analysis of how the system performs against keyword-stuffing and resume fraud.

## Technology Stack

- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Styling**: Tailwind CSS
- **Components**: UI components built with Radix UI primitives and styled for modern, high-contrast usability.
- **Icons**: Lucide React
- **Integration**: Fetches live data directly from the Scout FastAPI Backend (`http://localhost:8000`).

## Getting Started

First, ensure the backend API is running (see the root directory README for instructions).

Then, run the frontend development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

- `/src/app`: Contains all Next.js page routes (`/rank`, `/results`, `/candidate`, etc.).
- `/src/components`: Reusable React components (Navbar, UI primitives).
- `/src/lib`: Utility functions and API integration logic (`api.ts`).

## API Integration

The frontend expects the Scout backend API to be running on `http://localhost:8000`. Key endpoints utilized include:
- `POST /rank-candidates`: Submits JD text and retrieves the ranked list.
- `GET /candidate/{id}`: Retrieves deep-dive feature metadata for a specific candidate.

If your backend is hosted elsewhere, update the API base URL in `src/lib/api.ts`.
