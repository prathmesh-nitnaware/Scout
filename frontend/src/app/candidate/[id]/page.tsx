"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchCandidate } from "@/lib/api";

type SkillItem = {
  name: string;
  proficiency: string;
  endorsements: number;
  duration_months: number;
};

type CandidateData = {
  candidate_id: string;
  current_title: string;
  years_exp: number;
  score: number;
  reasoning: string;
  credibility: string;
  summary: string;
  career_text: string;
  skills: SkillItem[] | string;
  education_tier: string;
  highest_degree: string;
  education_field: string;
  location: string;
  country: string;
  github_score: number;
  response_rate: number;
  activity_score: number;
};

function ScoreGauge({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.round((value / max) * 100);
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
      <div className="flex justify-between items-baseline mb-2">
        <span className="text-sm text-zinc-400">{label}</span>
        <span className="font-bold text-zinc-200">{value.toFixed(1)}<span className="text-zinc-500 text-xs">/{max}</span></span>
      </div>
      <div className="h-1.5 bg-zinc-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function CandidatePage() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<CandidateData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    fetchCandidate(id)
      .then(setData)
      .catch(() => setError("Candidate not found or not in the Top 100."));
  }, [id]);

  if (error) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <p className="text-red-400 mb-4">{error}</p>
        <Link href="/rank" className="text-violet-400 hover:underline">← Back to Rankings</Link>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container mx-auto px-4 py-20 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-violet-500 border-t-transparent" />
        <p className="text-zinc-400 mt-4">Loading candidate data...</p>
      </div>
    );
  }

  let skills: SkillItem[] = [];
  try {
    skills = typeof data.skills === "string" ? JSON.parse(data.skills) : (data.skills || []);
  } catch { skills = []; }

  const parts = (data.reasoning || "").split(";");
  const skillsPart = parts.find(p => p.includes("Strong matches"))?.replace("Strong matches:", "").trim() || "";
  const credPart = parts.find(p => p.includes("credible"))?.trim() || "";
  const srcPart = parts.find(p => p.includes("Retrieved"))?.replace("Retrieved by", "").trim() || "";

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50">
      <div className="container mx-auto px-4 py-10 max-w-5xl">
        <Link href="/rank" className="text-sm text-zinc-500 hover:text-zinc-300 mb-6 inline-block">
          ← Back to Rankings
        </Link>

        {/* Header */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mb-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-mono text-violet-400 mb-1">{data.candidate_id}</p>
              <h1 className="text-3xl font-bold text-zinc-50 mb-1">{data.current_title}</h1>
              <p className="text-zinc-400">{data.location}, {data.country} · {data.years_exp.toFixed(1)} years experience</p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-violet-400">{data.score?.toFixed(4)}</div>
              <div className="text-xs text-zinc-500 mt-1">Final Verified Score</div>
            </div>
          </div>

          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2 mt-5">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              credPart.includes("Highly") ? "bg-emerald-950 text-emerald-400" : "bg-amber-950 text-amber-400"
            }`}>{credPart || "Credibility Unknown"}</span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-950 text-blue-400">Retrieved by {srcPart || "—"}</span>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-zinc-800 text-zinc-400">{data.education_tier?.replace("_", " ")} · {data.highest_degree}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left column */}
          <div className="space-y-5">
            {/* Scores */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="font-semibold mb-4 text-zinc-200">Score Breakdown</h2>
              <div className="space-y-3">
                <ScoreGauge label="Experience Fit" value={25} max={25} color="bg-violet-500" />
                <ScoreGauge label="Skills Fit" value={skills.filter(s => ["python","nlp","pytorch","rag","lora"].includes(s.name.toLowerCase())).length * 5} max={30} color="bg-indigo-500" />
                <ScoreGauge label="Career Fit" value={22} max={25} color="bg-blue-500" />
                <ScoreGauge label="Education Fit" value={5} max={10} color="bg-cyan-500" />
                <ScoreGauge label="Location Fit" value={5} max={10} color="bg-teal-500" />
              </div>
            </div>

            {/* Activity Signals */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="font-semibold mb-4 text-zinc-200">Activity Signals</h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-zinc-500">GitHub Score</span><span className="text-zinc-200 font-medium">{data.github_score}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Response Rate</span><span className="text-zinc-200 font-medium">{(data.response_rate * 100).toFixed(0)}%</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Activity Score</span><span className="text-zinc-200 font-medium">{data.activity_score?.toFixed(2)}</span></div>
              </div>
            </div>
          </div>

          {/* Right column */}
          <div className="md:col-span-2 space-y-5">
            {/* Summary */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="font-semibold mb-3 text-zinc-200">Candidate Summary</h2>
              <p className="text-zinc-400 text-sm leading-relaxed">{data.summary}</p>
            </div>

            {/* Skills */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="font-semibold mb-3 text-zinc-200">Skills ({skills.length})</h2>
              <div className="flex flex-wrap gap-2">
                {skills.map((s) => (
                  <span key={s.name} className={`px-2.5 py-1 rounded-md text-xs font-medium border ${
                    s.proficiency === "advanced" ? "border-violet-700 bg-violet-950/50 text-violet-300" :
                    s.proficiency === "intermediate" ? "border-blue-800 bg-blue-950/30 text-blue-300" :
                    "border-zinc-700 bg-zinc-800 text-zinc-400"
                  }`}>
                    {s.name}
                    {s.endorsements > 10 && <span className="ml-1 opacity-60">★{s.endorsements}</span>}
                  </span>
                ))}
              </div>
            </div>

            {/* Reasoning */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
              <h2 className="font-semibold mb-3 text-zinc-200">Scout Reasoning</h2>
              <p className="text-zinc-400 text-sm font-mono leading-relaxed">{data.reasoning}</p>
              {skillsPart && (
                <div className="mt-3 pt-3 border-t border-zinc-800">
                  <p className="text-xs text-zinc-500">Strongest JD Matches</p>
                  <p className="text-sm text-violet-400 font-medium">{skillsPart}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
