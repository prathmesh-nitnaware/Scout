import Link from "next/link";

const domainBadges = [
  "AI / ML Engineering", "Backend Engineering", "Data Engineering",
  "DevOps", "Product Management", "Security Engineering",
];

const phases = [
  { step: "01", name: "Validation", description: "Invalid and fraudulent profiles are eliminated before scoring begins.", color: "from-violet-600 to-indigo-600" },
  { step: "02", name: "Hybrid Retrieval", description: "Sparse keyword matching and dense semantic search run in parallel, capturing candidates each method misses independently.", color: "from-indigo-600 to-blue-600" },
  { step: "03", name: "Structured Scoring", description: "Candidates are evaluated across five dimensions: experience alignment, skills depth, career trajectory, education, and location fit.", color: "from-blue-600 to-cyan-600" },
  { step: "04", name: "Credibility Engine", description: "Claims are cross-referenced against actual career text. Candidates who list skills without mentioning them in their history are penalized.", color: "from-cyan-600 to-teal-600" },
  { step: "05", name: "Final Ranking", description: "A transparent, auditable formula combines all signals to produce a ranked shortlist with recruiter-readable explanations.", color: "from-teal-600 to-emerald-600" },
];

const metrics = [
  { label: "Candidates Processed", value: "100,000", sub: "Raw input" },
  { label: "Fraudulent Profiles Removed", value: "2,165", sub: "Validation engine" },
  { label: "High-Signal Candidates", value: "1,978", sub: "Retrieval pool" },
  { label: "Final Verified Shortlist", value: "100", sub: "Ranked output" },
];

const valueProps = [
  { icon: "🎯", title: "Beyond Keywords", body: "Traditional ATS systems rank by keyword overlap. A candidate who lists PyTorch five times ranks above someone who built production ML systems for six years. Scout evaluates evidence, not frequency." },
  { icon: "🔍", title: "Fraud-Resistant", body: "Scout's Credibility Engine detects resume inflation, skills-narrative contradictions, and keyword stuffing — automatically, without human review of every profile." },
  { icon: "📋", title: "Auditable Rankings", body: "Every score is mathematically traceable. Recruiters see exactly which dimension drove a candidate ranking — no black-box AI decisions." },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-zinc-800">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-violet-900/30 via-zinc-950 to-zinc-950" />
        <div className="relative container mx-auto px-4 py-28 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm text-violet-400 mb-8">
            <span className="h-2 w-2 rounded-full bg-violet-400 animate-pulse" />
            Hackathon Submission · India Runs Data &amp; AI Challenge
          </div>
          <h1 className="text-6xl sm:text-8xl font-extrabold tracking-tight mb-6 bg-gradient-to-br from-white via-zinc-200 to-zinc-500 bg-clip-text text-transparent">
            Scout
          </h1>
          <p className="text-2xl sm:text-3xl font-semibold text-zinc-200 max-w-2xl mx-auto mb-4 leading-snug">
            Find the right candidates beyond keyword matching.
          </p>
          <p className="text-zinc-400 max-w-2xl mx-auto mb-10 text-lg leading-relaxed">
            Traditional recruiting tools rank resumes based on keyword overlap. Scout evaluates candidate quality, career alignment, and evidence-backed expertise to surface trustworthy shortlists.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/rank" className="inline-flex items-center justify-center rounded-lg bg-violet-600 hover:bg-violet-700 px-8 py-3.5 font-semibold text-base transition-colors">
              Run Demo →
            </Link>
            <Link href="/architecture" className="inline-flex items-center justify-center rounded-lg border border-zinc-700 hover:border-zinc-500 px-8 py-3.5 font-semibold text-base transition-colors">
              View Architecture
            </Link>
          </div>
        </div>
      </section>

      {/* Domain-Agnostic Banner */}
      <section className="border-b border-zinc-800 bg-zinc-900/50 py-5">
        <div className="container mx-auto px-4">
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3">
            <span className="text-sm font-semibold text-amber-400 uppercase tracking-wide whitespace-nowrap">Prototype Demo</span>
            <span className="hidden md:block h-4 w-px bg-zinc-700" />
            <span className="text-sm text-zinc-400 text-center">
              Current deployment uses the challenge AI/ML dataset. The Scout framework is <strong className="text-zinc-300">domain-agnostic</strong> — configurable for any hiring domain.
            </span>
            <div className="flex flex-wrap gap-2 justify-center">
              {domainBadges.map((d) => (
                <span key={d} className="px-2.5 py-0.5 rounded-full text-xs bg-zinc-800 border border-zinc-700 text-zinc-400">{d}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Key Metrics */}
      <section className="border-b border-zinc-800 py-14">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {metrics.map((m) => (
              <div key={m.label} className="text-center">
                <div className="text-4xl font-bold text-violet-400 mb-1">{m.value}</div>
                <div className="font-medium text-zinc-200 mb-1">{m.label}</div>
                <div className="text-sm text-zinc-500">{m.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Props */}
      <section className="border-b border-zinc-800 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-3">Why Keyword Recruiting Fails</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">
              Traditional tools rank resumes. Scout evaluates candidate quality, career alignment, and evidence-backed expertise.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {valueProps.map((v) => (
              <div key={v.title} className="rounded-xl border border-zinc-800 bg-zinc-900 p-6">
                <div className="text-3xl mb-3">{v.icon}</div>
                <h3 className="font-bold text-lg text-zinc-100 mb-2">{v.title}</h3>
                <p className="text-zinc-400 text-sm leading-relaxed">{v.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline Overview */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold mb-3">How Scout Works</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              A five-stage pipeline that progressively filters, scores, and authenticates candidates.
            </p>
          </div>
          <div className="relative max-w-3xl mx-auto space-y-4">
            {phases.map((phase, i) => (
              <div key={phase.step} className="relative flex gap-6 items-start">
                {i < phases.length - 1 && (
                  <div className="absolute left-[1.75rem] top-14 h-full w-px bg-zinc-800" />
                )}
                <div className={`h-14 w-14 shrink-0 rounded-xl bg-gradient-to-br ${phase.color} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
                  {phase.step}
                </div>
                <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 flex-1 hover:border-zinc-600 transition-colors">
                  <h3 className="font-bold text-lg text-zinc-100 mb-1">{phase.name}</h3>
                  <p className="text-zinc-400 text-sm">{phase.description}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-12 flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/rank" className="inline-flex items-center justify-center rounded-lg bg-violet-600 hover:bg-violet-700 px-8 py-3 font-semibold transition-colors">
              Run Demo →
            </Link>
            <Link href="/results" className="inline-flex items-center justify-center rounded-lg border border-zinc-700 hover:border-zinc-500 px-8 py-3 font-semibold transition-colors">
              View Results &amp; Proof
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
