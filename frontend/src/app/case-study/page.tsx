import Link from "next/link";

export default function CaseStudyPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 py-12">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-3">Case Study</h1>
          <p className="text-zinc-400 text-lg">
            A deep dive into Scout's pipeline execution and fraud detection.
          </p>
        </div>

        <div className="space-y-16">
          {/* Section 1: Candidate Funnel */}
          <section>
            <h2 className="text-2xl font-bold mb-6 text-violet-400">1. Candidate Funnel</h2>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="text-center flex-1">
                <div className="text-3xl font-black text-zinc-100 mb-1">100,000</div>
                <div className="text-sm font-semibold text-zinc-400 mb-1">Raw Input</div>
              </div>
              <div className="text-zinc-600">→</div>
              <div className="text-center flex-1">
                <div className="text-3xl font-black text-zinc-100 mb-1">97,835</div>
                <div className="text-sm font-semibold text-zinc-400 mb-1">Validated</div>
              </div>
              <div className="text-zinc-600">→</div>
              <div className="text-center flex-1">
                <div className="text-3xl font-black text-zinc-100 mb-1">1,978</div>
                <div className="text-sm font-semibold text-zinc-400 mb-1">Retrieved</div>
              </div>
              <div className="text-zinc-600">→</div>
              <div className="text-center flex-1">
                <div className="text-3xl font-black text-violet-400 mb-1">100</div>
                <div className="text-sm font-semibold text-violet-300 mb-1">Ranked Output</div>
              </div>
            </div>
          </section>

          {/* Section 2: Trap Candidate Walkthrough */}
          <section>
            <h2 className="text-2xl font-bold mb-6 text-amber-400">2. Trap Candidate Walkthrough</h2>
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
              <div className="border-b border-zinc-800 bg-zinc-950/50 p-4">
                <h3 className="font-mono text-amber-400 font-bold">CAND_0000970</h3>
                <p className="text-sm text-zinc-400">Data Engineer claiming LoRA expertise.</p>
              </div>
              <div className="p-6 space-y-6">
                <div className="flex gap-4 items-start">
                  <div className="px-3 py-1 bg-zinc-800 text-zinc-300 rounded font-mono text-xs">Phase 3</div>
                  <div>
                    <strong className="text-zinc-200">Retrieved by TF-IDF</strong>
                    <p className="text-sm text-zinc-400 mt-1">Found highly-weighted term "LoRA" in candidate's skills array.</p>
                  </div>
                </div>
                <div className="flex gap-4 items-start">
                  <div className="px-3 py-1 bg-amber-900/50 text-amber-400 border border-amber-800 rounded font-mono text-xs">Phase 4</div>
                  <div>
                    <strong className="text-zinc-200">Career Mismatch Penalty</strong>
                    <p className="text-sm text-zinc-400 mt-1">Structured scoring detected title divergence from AI Engineer requirements.</p>
                  </div>
                </div>
                <div className="flex gap-4 items-start">
                  <div className="px-3 py-1 bg-red-900/50 text-red-400 border border-red-800 rounded font-mono text-xs">Phase 5</div>
                  <div>
                    <strong className="text-zinc-200">Skills-Narrative Contradiction</strong>
                    <p className="text-sm text-zinc-400 mt-1">Credibility Engine scanned career history text and found ZERO mentions of LoRA or fine-tuning.</p>
                  </div>
                </div>
                <div className="flex gap-4 items-start border-t border-zinc-800 pt-6">
                  <div className="px-3 py-1 bg-red-950 text-red-500 font-mono text-xs font-bold">Final</div>
                  <div>
                    <strong className="text-zinc-200">Removed from Shortlist</strong>
                    <p className="text-sm text-zinc-400 mt-1">Combined score fell below top 100 threshold due to severe credibility penalty.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Section 3: Why Scout Works */}
          <section>
            <h2 className="text-2xl font-bold mb-6 text-blue-400">3. Why Scout Works</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-5 rounded-lg border border-zinc-800 bg-zinc-900">
                <h3 className="font-bold text-zinc-200 mb-2">Validation</h3>
                <p className="text-sm text-zinc-400">Deterministically excludes impossible profiles (e.g. 15 YOE but graduated in 2022).</p>
              </div>
              <div className="p-5 rounded-lg border border-zinc-800 bg-zinc-900">
                <h3 className="font-bold text-zinc-200 mb-2">Hybrid Retrieval</h3>
                <p className="text-sm text-zinc-400">Combines TF-IDF and Tech MiniLM to maximize recall without semantic washout.</p>
              </div>
              <div className="p-5 rounded-lg border border-zinc-800 bg-zinc-900">
                <h3 className="font-bold text-zinc-200 mb-2">Structured Scoring</h3>
                <p className="text-sm text-zinc-400">Evaluates actual constraints (experience bounds, career progression) logically.</p>
              </div>
              <div className="p-5 rounded-lg border border-zinc-800 bg-zinc-900">
                <h3 className="font-bold text-zinc-200 mb-2">Credibility</h3>
                <p className="text-sm text-zinc-400">Cross-references skills against career narrative text to penalize inflation.</p>
              </div>
            </div>
          </section>

          {/* Section 4: Before vs After */}
          <section>
            <h2 className="text-2xl font-bold mb-6 text-emerald-400">4. Before vs After Ranking Snapshot</h2>
            <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-red-400 font-bold mb-4">Traditional ATS (Keyword Search)</h3>
                  <ul className="space-y-3">
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-red-500">❌</span> #1: Candidate with 50 generic skills listed.</li>
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-red-500">❌</span> #2: Marketing Manager who wrote "AI" 10 times.</li>
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-red-500">❌</span> #3: Data Engineer claiming unverified LoRA.</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-emerald-400 font-bold mb-4">Scout Output</h3>
                  <ul className="space-y-3">
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-emerald-500">✓</span> #1: 6.2 YOE Computer Vision Engineer.</li>
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-emerald-500">✓</span> #2: 5.6 YOE CV Engineer with verified FAISS.</li>
                    <li className="flex gap-2 text-sm text-zinc-400"><span className="text-emerald-500">✓</span> #3: 5.7 YOE ML Engineer with embeddings history.</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
