const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE_URL}/metrics`);
  return res.json();
}

/**
 * Run the live ranking pipeline via the hardened /rank-candidates endpoint.
 * Falls back to the static /rank endpoint if jd_text is empty.
 */
export async function runRanking(jd_text?: string) {
  if (jd_text && jd_text.trim().length > 0) {
    // Use the live hardened endpoint with real JD parsing
    const res = await fetch(`${API_BASE_URL}/rank-candidates`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text }),
    });
    const data = await res.json();
    // Normalise: wrap in {candidates:[...]} if already an array
    return data;
  } else {
    // Fallback: return the pre-computed static ranking
    const res = await fetch(`${API_BASE_URL}/rank`, { method: "POST" });
    return res.json();
  }
}

export async function fetchCandidate(id: string) {
  const res = await fetch(`${API_BASE_URL}/candidate/${id}`);
  if (!res.ok) {
    throw new Error("Candidate not found");
  }
  return res.json();
}
