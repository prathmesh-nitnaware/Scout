"use client";

import { useState } from "react";
import Link from "next/link";
import { runRanking } from "@/lib/api";

type Candidate = {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
  current_title?: string;
  years_exp?: number;
  credibility?: string;
};

type RetrievalStats = {
  tfidf_pool_size: number;
  minilm_pool_size: number;
  union_pool_size: number;
  both_retrieved: number;
};

const domainBadges = [
  "AI / ML Engineering", "Backend Engineering", "Data Engineering",
  "DevOps", "Product Management", "Security Engineering",
];

const PHASE_LABELS = [
  { label: "Validating candidate pool...", icon: "🛡️" },
  { label: "Running TF-IDF retrieval (Top 1,000)...", icon: "🔎" },
  { label: "Running Technical MiniLM retrieval (Top 1,000)...", icon: "🧠" },
  { label: "Building union pool...", icon: "🔗" },
  { label: "Applying Structured Scoring (5 domains)...", icon: "📊" },
  { label: "Running Credibility Engine...", icon: "🔬" },
  { label: "Generating final rankings with reasoning...", icon: "🏆" },
];

function ScoreBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 bg-zinc-700 rounded-full overflow-hidden">
        <div className="h-full bg-violet-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-zinc-400 tabular-nums">{value.toFixed(4)}</span>
    </div>
  );
}

export default function RankPage() {
  const [jdText, setJdText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [phaseIdx, setPhaseIdx] = useState(-1);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [retrievalStats, setRetrievalStats] = useState<RetrievalStats | null>(null);
  const [jdExpParsed, setJdExpParsed] = useState<{ min_years: number; max_years: number } | null>(null);
  const [error, setError] = useState("");

  const avgScore = candidates.length > 0 ? (candidates.reduce((s, c) => s + c.score, 0) / candidates.length).toFixed(4) : "—";
  const highCred = candidates.filter(c => c.credibility?.includes("High")).length;

  async function handleRun() {
    setIsLoading(true);
    setError("");
    setCandidates([]);
    setRetrievalStats(null);
    setJdExpParsed(null);
    for (let i = 0; i < PHASE_LABELS.length; i++) {
      setPhaseIdx(i);
      await new Promise((r) => setTimeout(r, 550));
    }
    try {
      const data = await runRanking(jdText);
      setCandidates(data.candidates || []);
      if (data.retrieval_stats) setRetrievalStats(data.retrieval_stats);
      if (data.jd_experience_parsed) setJdExpParsed(data.jd_experience_parsed);
    } catch {
      setError("Could not connect to the Scout API. Ensure the FastAPI server is running on port 8000.");
    } finally {
      setIsLoading(false);
      setPhaseIdx(-1);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Rank Candidates</h1>
            <p className="text-zinc-400">
              Paste a job description to run the Scout pipeline and surface your Top 100 verified candidates.
            </p>
          </div>

          {/* Domain-Agnostic Banner */}
          <div className="rounded-xl border border-amber-800/50 bg-amber-950/20 p-4 mb-8">
            <div className="flex flex-wrap items-start gap-3">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-wide bg-amber-900/40 px-2 py-0.5 rounded mt-0.5">Prototype Demo</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-zinc-300 mb-2">
                  Current deployment uses the challenge AI/ML Engineering dataset. The Scout ranking framework is <strong>domain-agnostic</strong> — configurable via the JD Profile Layer for any hiring domain.
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {domainBadges.map((d) => (
                    <span key={d} className="px-2 py-0.5 rounded text-xs bg-zinc-800 border border-zinc-700 text-zinc-400">{d}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* JD Input */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mb-8">
            <label className="block text-sm font-medium text-zinc-300 mb-3">Job Description</label>
            <textarea
              className="w-full h-36 bg-zinc-950 border border-zinc-700 rounded-lg p-4 text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-violet-500 resize-none"
              placeholder="Paste a Job Description here... (Demo mode uses the pre-loaded AI/ML Engineering JD from the challenge dataset)"
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
            <div className="flex items-center gap-4 mt-4">
              <button
                onClick={handleRun}
                disabled={isLoading}
                className="inline-flex items-center gap-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2.5 font-semibold text-sm transition-colors"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                    </svg>
                    Running Pipeline...
                  </>
                ) : "Run Scout Pipeline →"}
              </button>
              <span className="text-xs text-zinc-500">Demo uses the pre-loaded AI/ML Engineering JD</span>
            </div>
          </div>

          {/* Loading Phase Tracker */}
          {isLoading && (
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mb-8">
              <h3 className="text-sm font-semibold text-zinc-300 mb-4">Pipeline Progress</h3>
              <div className="space-y-2.5">
                {PHASE_LABELS.map(({ label, icon }, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <div className={`h-6 w-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs transition-all ${
                      i < phaseIdx ? "bg-emerald-600" : i === phaseIdx ? "bg-violet-600 animate-pulse" : "bg-zinc-800"
                    }`}>
                      {i < phaseIdx ? "✓" : icon}
                    </div>
                    <span className={i === phaseIdx ? "text-zinc-100 font-medium" : i < phaseIdx ? "text-zinc-500 line-through" : "text-zinc-600"}>
                      {label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-800 bg-red-950/30 p-4 mb-8 text-red-400 text-sm">{error}</div>
          )}

          {/* Dashboard Cards */}
          {candidates.length > 0 && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                  { label: "Final Shortlist", value: candidates.length.toString(), sub: "Verified candidates" },
                  { label: "Average Score", value: avgScore, sub: "Out of 1.0000" },
                  { label: "High Credibility", value: `${highCred}`, sub: "Cred score ≥ 90" },
                  { label: "Union Pool", value: retrievalStats ? retrievalStats.union_pool_size.toLocaleString() : "—", sub: "TF-IDF + MiniLM" },
                ].map((card) => (
                  <div key={card.label} className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 text-center">
                    <div className="text-3xl font-bold text-violet-400 mb-1">{card.value}</div>
                    <div className="text-sm font-medium text-zinc-200">{card.label}</div>
                    <div className="text-xs text-zinc-500 mt-0.5">{card.sub}</div>
                  </div>
                ))}
              </div>

              {/* Retrieval Stats + JD Parsed */}
              {(retrievalStats || jdExpParsed) && (
                <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 mb-6 flex flex-wrap gap-6 text-sm">
                  {jdExpParsed && (
                    <div>
                      <span className="text-zinc-500 text-xs uppercase tracking-wide">JD Experience Parsed</span>
                      <div className="font-semibold text-violet-400 mt-0.5">{jdExpParsed.min_years}–{jdExpParsed.max_years} years</div>
                    </div>
                  )}
                  {retrievalStats && (
                    <>
                      <div>
                        <span className="text-zinc-500 text-xs uppercase tracking-wide">TF-IDF Pool</span>
                        <div className="font-semibold text-zinc-300 mt-0.5">{retrievalStats.tfidf_pool_size.toLocaleString()}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500 text-xs uppercase tracking-wide">MiniLM Pool</span>
                        <div className="font-semibold text-zinc-300 mt-0.5">{retrievalStats.minilm_pool_size.toLocaleString()}</div>
                      </div>
                      <div>
                        <span className="text-zinc-500 text-xs uppercase tracking-wide">Retrieved by Both</span>
                        <div className="font-semibold text-emerald-400 mt-0.5">{retrievalStats.both_retrieved} <span className="text-zinc-500 font-normal text-xs">(1.2× boost)</span></div>
                      </div>
                    </>
                  )}
                </div>
              )}


              {/* Results Table */}
              <div className="rounded-xl border border-zinc-800 overflow-hidden">
                <div className="bg-zinc-900 border-b border-zinc-800 px-5 py-4 flex items-center justify-between">
                  <h2 className="font-bold text-zinc-100">Top {candidates.length} Ranked Candidates</h2>
                  <span className="text-xs text-zinc-500">Sorted by Final Verified Score</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-zinc-900/50 border-b border-zinc-800">
                      <tr>
                        {["Rank", "Candidate", "Title", "Experience", "Score", "Credibility", "Reasoning", ""].map(h => (
                          <th key={h} className="text-left px-4 py-3 text-zinc-400 font-medium text-xs uppercase tracking-wider">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {candidates.map((c, i) => {
                        const reasoningShort = c.reasoning
                          ?.split(";")
                          .find(p => p.includes("Strong matches") || p.includes("General skills"))
                          ?.trim() || "";
                        return (
                          <tr key={c.candidate_id} className={`border-t border-zinc-800/50 hover:bg-zinc-900/60 transition-colors ${i < 3 ? "bg-violet-950/10" : ""}`}>
                            <td className="px-4 py-3.5">
                              <span className={`font-bold ${i === 0 ? "text-amber-400" : i === 1 ? "text-zinc-300" : i === 2 ? "text-amber-700" : "text-zinc-500"}`}>
                                #{c.rank}
                              </span>
                            </td>
                            <td className="px-4 py-3.5 font-mono text-xs text-violet-400 whitespace-nowrap">{c.candidate_id}</td>
                            <td className="px-4 py-3.5 text-zinc-200 whitespace-nowrap">{c.current_title || "—"}</td>
                            <td className="px-4 py-3.5 text-zinc-400 whitespace-nowrap">{c.years_exp ? `${c.years_exp.toFixed(1)}y` : "—"}</td>
                            <td className="px-4 py-3.5"><ScoreBar value={c.score} /></td>
                            <td className="px-4 py-3.5">
                              <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ${
                                c.credibility?.includes("High") ? "bg-emerald-950 text-emerald-400" : "bg-amber-950 text-amber-400"
                              }`}>
                                {c.credibility || "—"}
                              </span>
                            </td>
                            <td className="px-4 py-3.5 max-w-xs">
                              <span className="text-xs text-zinc-500 leading-relaxed">{reasoningShort}</span>
                            </td>
                            <td className="px-4 py-3.5">
                              <Link href={`/candidate/${c.candidate_id}`} className="text-xs text-violet-400 hover:text-violet-300 whitespace-nowrap">
                                View Details →
                              </Link>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
}
