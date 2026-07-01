import Link from "next/link";

const top10 = [
  { rank: 1, id: "CAND_0005260", title: "Senior NLP Engineer", exp: 5.2, score: 0.7822, cred: "High" },
  { rank: 2, id: "CAND_0094759", title: "Lead AI Engineer", exp: 8.6, score: 0.7424, cred: "High" },
  { rank: 3, id: "CAND_0018499", title: "Senior Machine Learning Engineer", exp: 7.2, score: 0.7418, cred: "High" },
  { rank: 4, id: "CAND_0008425", title: "Senior NLP Engineer", exp: 7.8, score: 0.7377, cred: "High" },
  { rank: 5, id: "CAND_0092278", title: "Senior NLP Engineer", exp: 6.8, score: 0.7314, cred: "High" },
  { rank: 6, id: "CAND_0071974", title: "Senior AI Engineer", exp: 7.8, score: 0.7264, cred: "High" },
  { rank: 7, id: "CAND_0055905", title: "Senior Machine Learning Engineer", exp: 8.1, score: 0.7243, cred: "High" },
  { rank: 8, id: "CAND_0033861", title: "Senior NLP Engineer", exp: 8.0, score: 0.7179, cred: "High" },
  { rank: 9, id: "CAND_0046525", title: "Senior Machine Learning Engineer", exp: 6.1, score: 0.6964, cred: "High" },
  { rank: 10, id: "CAND_0046064", title: "Senior NLP Engineer", exp: 8.9, score: 0.6862, cred: "High" },
];

const journeyStages = [
  { count: "100,000", label: "Raw Candidates", reduction: null, note: "Unfiltered JSONL input — includes honeypots and irrelevant profiles", color: "border-zinc-700" },
  { count: "97,835", label: "Validated", reduction: "−2.2%", note: "Honeypot profiles removed by the Validation Engine", color: "border-violet-700" },
  { count: "1,978", label: "Retrieved", reduction: "Top 2%", note: "High-recall union pool from TF-IDF and Technical MiniLM", color: "border-indigo-700" },
  { count: "100", label: "Final Shortlist", reduction: "Top 0.1%", note: "Structured scoring + credibility verification applied", color: "border-emerald-700" },
];

const benchmarks = [
  { method: "TF-IDF", result: "20/20", verdict: "pass", note: "Vulnerable to keyword stuffing" },
  { method: "Full JD MiniLM", result: "0/20", verdict: "fail", note: "Semantic washout from HR boilerplate" },
  { method: "Technical JD MiniLM", result: "20/20", verdict: "pass", note: "Condensed JD restores relevance" },
  { method: "Hybrid (Scout)", result: "20/20", verdict: "pass", note: "Captures distinct, non-overlapping cohorts" },
];

const trapPhases = [
  {
    phase: "Phase 3 — Retrieval",
    status: "warning",
    icon: "⚠️",
    title: "Retrieved by TF-IDF",
    detail: "The term \"LoRA\" appears rarely in the dataset, giving it high IDF weight. TF-IDF ranked this candidate in the top 5% (#5,406) purely on string match.",
  },
  {
    phase: "Phase 4 — Structured Scoring",
    status: "warning",
    icon: "📉",
    title: "Career Mismatch Penalty",
    detail: "Structured scorer identified \"Data Engineer\" as a poor fit for the target AI Engineer role. Career Fit component applied a penalty — score dropped significantly.",
  },
  {
    phase: "Phase 5 — Credibility Engine",
    status: "fail",
    icon: "🚫",
    title: "Skills-Narrative Contradiction",
    detail: "\"LoRA\" was listed in the skills dropdown. The credibility engine searched the candidate's full career history and summary — LoRA was never mentioned. Penalty applied.",
  },
  {
    phase: "Final Outcome",
    status: "eliminated",
    icon: "❌",
    title: "Removed from Final Shortlist",
    detail: "Combined score dropped below the Top 100 threshold. The candidate was excluded from submission_final.csv with full audit trail.",
  },
];

export default function ResultsPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">
      <div className="container mx-auto px-4 py-12 max-w-5xl">

        <h1 className="text-4xl font-bold mb-2">Results &amp; Proof</h1>
        <p className="text-zinc-400 mb-12 max-w-2xl">
          Evidence that Scout surfaces genuinely qualified candidates and systematically eliminates resume fraud.
        </p>

        {/* Section A — Candidate Journey */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">Candidate Journey</h2>
          <p className="text-zinc-400 mb-8 text-sm">100,000 candidates reduced to a verified shortlist of 100 through progressive quality gates.</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {journeyStages.map((s, i) => (
              <div key={s.label} className="relative">
                <div className={`rounded-xl border ${s.color} bg-zinc-900 p-5 h-full`}>
                  {s.reduction && (
                    <div className="text-xs font-semibold text-emerald-400 mb-1">{s.reduction}</div>
                  )}
                  <div className="text-3xl font-bold text-zinc-100 mb-1">{s.count}</div>
                  <div className="font-semibold text-zinc-300 mb-2">{s.label}</div>
                  <p className="text-xs text-zinc-500 leading-relaxed">{s.note}</p>
                </div>
                {i < journeyStages.length - 1 && (
                  <div className="hidden md:flex absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-zinc-600 text-lg">›</div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Section B — Trap Case Study */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">How Scout Defeats Resume Inflation</h2>
          <p className="text-zinc-400 mb-2 text-sm max-w-2xl">
            Candidate <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-red-300 text-xs">CAND_0000970</code> — a Data Engineer who listed "LoRA" in their skills without a single mention in their career history.
          </p>
          <div className="text-xs text-zinc-600 mb-8">Real case from the challenge dataset. No manual intervention required.</div>

          <div className="space-y-3">
            {trapPhases.map((p) => (
              <div
                key={p.phase}
                className={`rounded-xl border p-5 flex gap-4 items-start ${
                  p.status === "eliminated" ? "border-red-900 bg-red-950/20" :
                  p.status === "fail" ? "border-red-800 bg-red-950/10" :
                  "border-amber-800 bg-amber-950/10"
                }`}
              >
                <span className="text-2xl shrink-0 mt-0.5">{p.icon}</span>
                <div>
                  <div className="text-xs font-mono text-zinc-500 mb-1">{p.phase}</div>
                  <div className="font-semibold text-zinc-100 mb-1">{p.title}</div>
                  <p className="text-sm text-zinc-400 leading-relaxed">{p.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section C — Retrieval Benchmark */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-2">Retrieval Experiment Results</h2>
          <p className="text-zinc-400 mb-8 text-sm max-w-2xl">
            We benchmarked three retrieval strategies before selecting the hybrid approach. <strong className="text-zinc-300">Full JD MiniLM failed completely</strong> — 1,500 words of HR boilerplate drowned out 50 words of technical requirements.
          </p>
          <div className="rounded-xl border border-zinc-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-zinc-900 border-b border-zinc-800">
                <tr>
                  <th className="text-left px-5 py-3 text-zinc-400 font-medium">Retrieval Method</th>
                  <th className="text-left px-5 py-3 text-zinc-400 font-medium">Relevant in Top 20</th>
                  <th className="text-left px-5 py-3 text-zinc-400 font-medium">Finding</th>
                </tr>
              </thead>
              <tbody>
                {benchmarks.map((b) => (
                  <tr key={b.method} className="border-t border-zinc-800/50">
                    <td className="px-5 py-3.5 font-medium text-zinc-200">{b.method}</td>
                    <td className="px-5 py-3.5">
                      <span className={`font-bold text-base ${b.verdict === "pass" ? "text-emerald-400" : "text-red-400"}`}>
                        {b.result}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-zinc-500 text-sm">{b.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 rounded-lg border border-indigo-800 bg-indigo-950/20 p-4 text-sm text-indigo-300">
            <strong>Key finding:</strong> TF-IDF and Technical MiniLM found completely different candidate cohorts (0% overlap in Top 20). Combining both methods maximizes recall without sacrificing precision.
          </div>
        </section>

        {/* Section D — Top 10 Snapshot */}
        <section>
          <h2 className="text-2xl font-bold mb-2">Top Candidate Snapshot</h2>
          <p className="text-zinc-400 mb-6 text-sm">The final Top 10 from the Scout pipeline. All verified through structured scoring and credibility analysis.</p>
          <div className="rounded-xl border border-zinc-800 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-zinc-900 border-b border-zinc-800">
                <tr>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Rank</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Title</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Experience</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Credibility</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium">Score</th>
                  <th className="text-left px-4 py-3 text-zinc-400 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {top10.map((c, i) => (
                  <tr key={c.id} className={`border-t border-zinc-800/50 hover:bg-zinc-900/50 transition-colors ${i < 3 ? "bg-violet-950/10" : ""}`}>
                    <td className="px-4 py-3">
                      <span className={`font-bold ${i === 0 ? "text-amber-400 text-base" : i < 3 ? "text-zinc-300" : "text-zinc-500"}`}>#{c.rank}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-zinc-200">{c.title}</div>
                      <div className="text-xs font-mono text-zinc-600">{c.id}</div>
                    </td>
                    <td className="px-4 py-3 text-zinc-400">{c.exp.toFixed(1)} years</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400">
                        {c.cred} (≥90)
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 bg-zinc-700 rounded-full overflow-hidden">
                          <div className="h-full bg-violet-500 rounded-full" style={{ width: `${c.score * 100}%` }} />
                        </div>
                        <span className="text-xs text-zinc-400 tabular-nums">{c.score.toFixed(4)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/candidate/${c.id}`} className="text-xs text-violet-400 hover:text-violet-300 whitespace-nowrap">
                        View →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 text-center">
            <Link href="/rank" className="inline-flex items-center justify-center rounded-lg bg-violet-600 hover:bg-violet-700 px-6 py-2.5 text-sm font-semibold transition-colors">
              Run the Full Pipeline →
            </Link>
          </div>
        </section>

      </div>
    </div>
  );
}
