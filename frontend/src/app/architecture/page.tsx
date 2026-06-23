export default function ArchitecturePage() {
  const stages = [
    {
      num: "01",
      name: "Validation Engine",
      icon: "🛡️",
      color: "border-violet-700 bg-violet-950/20",
      badge: "bg-violet-900/50 text-violet-300",
      description:
        "Applies deterministic rule logic to eliminate logically impossible profiles before any embedding or scoring is performed.",
      rules: [
        "Experience vs. graduation date conflicts",
        "Impossible salary-to-role combinations",
        "Behavioral clone detection",
      ],
      output: "97,835 valid candidates",
    },
    {
      num: "02",
      name: "Hybrid Retrieval",
      icon: "🔍",
      color: "border-indigo-700 bg-indigo-950/20",
      badge: "bg-indigo-900/50 text-indigo-300",
      description:
        "Dual-pipeline retrieval combining sparse TF-IDF and dense sentence embedding to maximize recall and capture diverse high-quality cohorts.",
      rules: [
        "TF-IDF: exact keyword matching (Top 1,000)",
        "Technical MiniLM: semantic embedding of condensed JD (Top 1,000)",
        "Union pool ensures 0% signal loss between methods",
      ],
      output: "1,978 candidate union pool",
    },
    {
      num: "03",
      name: "Structured Scoring",
      icon: "📊",
      color: "border-blue-700 bg-blue-950/20",
      badge: "bg-blue-900/50 text-blue-300",
      description:
        "Five-domain constraint-based scoring evaluates candidate claims against explicit JD requirements with transparent, auditable weights.",
      rules: [
        "Experience Fit (25%) — ideal range 5–9 years",
        "Skills Fit (30%) — endorsements + duration weighting",
        "Career Fit (25%) — title and role progression",
        "Education Fit (10%) — degree and field bonus",
        "Location Fit (10%) — geo-logistics alignment",
      ],
      output: "Score 0–100 per candidate",
    },
    {
      num: "04",
      name: "Credibility Engine",
      icon: "🔬",
      color: "border-cyan-700 bg-cyan-950/20",
      badge: "bg-cyan-900/50 text-cyan-300",
      description:
        "Cross-references candidate claims against their actual career narrative text using deterministic Python logic — no LLM calls.",
      rules: [
        "Skills-Narrative Contradiction: claimed skill absent from career text",
        "Skill Inflation: too many skills for years of experience",
        "Keyword Stuffing: skill count exceeds reasonable ceiling",
        "Inflated Title: senior titles with junior tenure",
        "Career Instability: excessive job-hopping ratio",
      ],
      output: "Credibility score 0–100 multiplier",
    },
    {
      num: "05",
      name: "Final Ranker",
      icon: "🏆",
      color: "border-teal-700 bg-teal-950/20",
      badge: "bg-teal-900/50 text-teal-300",
      description:
        "Combines all signals into a single, transparent score formula. Produces submission CSV with reasoning strings.",
      rules: [
        "Formula: Structured × (Credibility / 100) × Retrieval Confidence",
        "Retrieval Confidence: 1.15× if retrieved by BOTH TF-IDF and MiniLM",
        "Tie-breaking: candidate_id ascending",
        "Pure scaled score: final_score / 100 (no artificial floor)",
      ],
      output: "Top 100 verified candidates",
    },
  ];

  const benchmarks = [
    { method: "TF-IDF", top20: "20 / 20", note: "Vulnerable to keyword stuffing" },
    { method: "Full JD MiniLM", top20: "0 / 20", note: "Semantic washout from HR boilerplate" },
    { method: "Technical JD MiniLM", top20: "20 / 20", note: "Condensed JD restores relevance" },
    { method: "Hybrid (Scout)", top20: "20 / 20", note: "Captures distinct cohorts from both methods" },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-4xl font-bold mb-2">Architecture</h1>
        <p className="text-zinc-400 mb-12 max-w-2xl">
          Scout's five-stage pipeline treats the candidate dataset as inherently adversarial. Each stage enforces progressively stricter quality gates.
        </p>

        {/* Pipeline flow */}
        <div className="space-y-4 mb-16">
          {stages.map((stage, i) => (
            <div key={stage.num}>
              <div className={`rounded-xl border ${stage.color} p-6`}>
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{stage.icon}</div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${stage.badge}`}>{stage.num}</span>
                      <h2 className="text-xl font-bold">{stage.name}</h2>
                    </div>
                    <p className="text-zinc-400 text-sm mb-3">{stage.description}</p>
                    <ul className="space-y-1">
                      {stage.rules.map((r) => (
                        <li key={r} className="flex items-start gap-2 text-sm text-zinc-400">
                          <span className="text-zinc-600 mt-0.5">·</span>
                          {r}
                        </li>
                      ))}
                    </ul>
                    <div className="mt-4 pt-3 border-t border-zinc-800/50 text-xs font-medium text-zinc-500">
                      Output: <span className="text-zinc-300">{stage.output}</span>
                    </div>
                  </div>
                </div>
              </div>
              {i < stages.length - 1 && (
                <div className="flex justify-center py-2 text-zinc-700">
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Retrieval benchmark */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
          <h2 className="text-xl font-bold mb-4">Retrieval Benchmark</h2>
          <p className="text-zinc-400 text-sm mb-5">
            Empirical comparison of relevant roles found in Top 20 results per method.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="text-left py-2 pr-6 text-zinc-400 font-medium">Method</th>
                  <th className="text-left py-2 pr-6 text-zinc-400 font-medium">Relevant in Top 20</th>
                  <th className="text-left py-2 text-zinc-400 font-medium">Notes</th>
                </tr>
              </thead>
              <tbody>
                {benchmarks.map((b) => (
                  <tr key={b.method} className="border-t border-zinc-800/50">
                    <td className="py-3 pr-6 font-medium text-zinc-200">{b.method}</td>
                    <td className="py-3 pr-6">
                      <span className={`font-bold ${b.top20.startsWith("0") ? "text-red-400" : "text-emerald-400"}`}>
                        {b.top20}
                      </span>
                    </td>
                    <td className="py-3 text-zinc-500">{b.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
