export default function AboutPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">
      <div className="container mx-auto px-4 py-12 max-w-3xl">
        <h1 className="text-4xl font-bold mb-2">About Scout</h1>
        <p className="text-zinc-400 mb-12">
          The engineering story behind a deterministic candidate ranking engine.
        </p>

        <div className="space-y-12">

          {/* Semantic Washout */}
          <section>
            <div className="inline-block px-3 py-1 rounded-full bg-violet-900/40 border border-violet-700/50 text-violet-400 text-xs font-semibold uppercase tracking-wide mb-4">
              Key Innovation
            </div>
            <h2 className="text-2xl font-bold mb-3">The Semantic Washout Discovery</h2>
            <p className="text-zinc-400 leading-relaxed mb-4">
              When we first embedded the full Job Description using{" "}
              <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-violet-300 text-sm">all-MiniLM-L6-v2</code>, the Top 20 results returned Mechanical Engineers, Civil Engineers, and HR Managers. Not a single ML Engineer appeared.
            </p>
            <p className="text-zinc-400 leading-relaxed mb-4">
              The cause: the 1,500-word JD contained extensive company descriptions, remote work policies, compensation details, and HR boilerplate. The embedding model's single dense vector became dominated by this generic context, completely washing out the 50 words of actual technical requirements.
            </p>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 mb-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="rounded-lg bg-red-950/30 border border-red-800 p-4">
                  <div className="text-red-400 font-semibold mb-2">❌ Full JD Embedding</div>
                  <div className="text-zinc-400">1,500 words: company culture, remote policy, benefits, compensation, legal boilerplate</div>
                  <div className="mt-3 text-xs text-zinc-500">Result: <span className="text-red-400 font-semibold">0/20 relevant roles</span></div>
                </div>
                <div className="rounded-lg bg-emerald-950/30 border border-emerald-800 p-4">
                  <div className="text-emerald-400 font-semibold mb-2">✓ Technical JD Embedding</div>
                  <div className="text-zinc-400">50 words: required skills, target roles, preferred experience only</div>
                  <div className="mt-3 text-xs text-zinc-500">Result: <span className="text-emerald-400 font-semibold">20/20 relevant roles</span></div>
                </div>
              </div>
            </div>

            <div className="rounded-lg border-l-4 border-violet-500 pl-4 py-2 bg-zinc-900/50">
              <h3 className="font-semibold text-zinc-200 mb-1">Why This Matters</h3>
              <p className="text-sm text-zinc-400 leading-relaxed">
                Most recruiting systems embed entire job descriptions. This causes technical requirements to be diluted by corporate language — systematically surfacing culturally-worded candidates instead of technically-qualified ones. Scout demonstrated this experimentally and solved it by separating technical requirements from organizational context before embedding. This is not a minor optimization: it is the difference between 0% and 100% retrieval precision.
              </p>
            </div>
          </section>

          {/* Hybrid Retrieval */}
          <section>
            <h2 className="text-2xl font-bold mb-3 text-indigo-400">Why Hybrid Retrieval?</h2>
            <p className="text-zinc-400 leading-relaxed mb-3">
              After fixing the embedding prompt, we discovered that the overlap between TF-IDF's Top 20 and Technical MiniLM's Top 20 was exactly{" "}
              <strong className="text-zinc-200">0%</strong>. The two methods found completely different, highly qualified candidates.
            </p>
            <p className="text-zinc-400 leading-relaxed">
              TF-IDF retrieved candidates who used the exact same technical vocabulary as the JD. MiniLM retrieved candidates with strong generalized semantic ML profiles — engineers who built production systems without necessarily using those exact keywords. A union of both methods maximizes recall without sacrificing precision.
            </p>
          </section>

          {/* Anti-Fraud */}
          <section>
            <h2 className="text-2xl font-bold mb-3 text-blue-400">Anti-Keyword-Stuffing Strategy</h2>
            <p className="text-zinc-400 leading-relaxed mb-3">
              TF-IDF's strength — exact keyword matching — is also its vulnerability. A Data Engineer who lists "LoRA" in a skills dropdown ranks in the top 5% purely on that single term.
            </p>
            <p className="text-zinc-400 leading-relaxed mb-3">
              Scout's Credibility Engine closes this gap. It searches the candidate's actual career text — multi-paragraph job descriptions they wrote — for corroborating evidence of every claimed skill. No mention of fine-tuning, no mention of LLMs? The skill is flagged as unverified and a penalty is applied.
            </p>
            <p className="text-zinc-400 leading-relaxed">
              This approach catches fraud that structured scoring alone cannot detect: candidates who pick every item in a skills dropdown but never actually discuss those technologies in their career history.
            </p>
          </section>

          {/* No LLM */}
          <section>
            <h2 className="text-2xl font-bold mb-3 text-cyan-400">Why No Runtime LLM Calls?</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                { icon: "🔁", title: "Reproducibility", desc: "LLM responses are stochastic. A candidate could rank #5 today and #15 tomorrow without changing their resume — unacceptable for hiring." },
                { icon: "💸", title: "Cost at Scale", desc: "GPT-4 on 100,000 profiles costs hundreds of dollars per run. Scout's entire pipeline runs on a standard CPU in seconds." },
                { icon: "⚡", title: "Latency", desc: "API rate limits make real-time candidate ranking across large pools prohibitively slow." },
                { icon: "🔍", title: "Auditability", desc: "Scout can pinpoint exactly which rule caused a score deduction — critical for defensible, explainable hiring decisions." },
              ].map((item) => (
                <div key={item.title} className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <h3 className="font-semibold text-zinc-200 mb-1">{item.title}</h3>
                  <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Pipeline results table */}
          <section>
            <h2 className="text-2xl font-bold mb-4 text-teal-400">Pipeline Results</h2>
            <div className="rounded-xl border border-zinc-800 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-zinc-900 border-b border-zinc-800">
                  <tr>
                    <th className="text-left px-5 py-3 text-zinc-400 font-medium">Stage</th>
                    <th className="text-right px-5 py-3 text-zinc-400 font-medium">Candidates</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ["Raw Dataset", "100,000"],
                    ["After Validation", "97,835"],
                    ["Union Retrieval Pool", "1,978"],
                    ["Final Ranked Output", "100"],
                  ].map(([stage, count]) => (
                    <tr key={stage} className="border-t border-zinc-800/50">
                      <td className="px-5 py-3 text-zinc-300">{stage}</td>
                      <td className="px-5 py-3 text-right font-mono font-bold text-violet-400">{count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
