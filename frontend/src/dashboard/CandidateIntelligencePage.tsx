import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, CalendarClock, CheckCircle2, Circle, FilePenLine, Sparkles, Target } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { ProgressBar } from "../components/ui/ProgressBar";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { usePageMeta } from "../hooks/usePageMeta";

const defaultChecklist = [
  { task: "Review distributed systems notes", done: true },
  { task: "Practice STAR format responses", done: false },
  { task: "Submit final availability preference", done: false },
  { task: "Upload portfolio examples", done: true },
];

export default function CandidateIntelligencePage() {
  const [loading, setLoading] = useState(true);
  const [checklist, setChecklist] = useState(defaultChecklist);

  usePageMeta("Candidate Intelligence Dashboard | Intervux AI", "AI-powered candidate command center with next actions, interview countdown, and intelligence recommendations.");

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 700);
    return () => window.clearTimeout(timer);
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <section className="rounded-[2rem] bg-gradient-to-r from-[#004ac6] to-[#2563eb] px-6 py-6 text-white shadow-lg">
        <p className="text-sm text-blue-100">Welcome back, Vishal</p>
        <h1 className="mt-1 font-[Manrope] text-3xl font-bold tracking-tight">Your candidate intelligence workspace</h1>
        <p className="mt-2 max-w-2xl text-sm text-blue-100">Intervux AI refreshed your interview strategy using recruiter calibration trends and recent performance telemetry.</p>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Next Interview" value="16h 24m" change="Tomorrow at 10:30 AM" />
        <StatCard label="Readiness Score" value="89" change="+6 pts this week" />
        <StatCard label="AI Confidence" value="93%" change="Strong trajectory" />
        <StatCard label="Task Completion" value={`${Math.round((checklist.filter((c) => c.done).length / checklist.length) * 100)}%`} change="Checklist progress" trend="down" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Next interview countdown" subtitle="Senior Backend Engineer • Technical panel" className="xl:col-span-2">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl bg-[#f2f4f6] p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Countdown</p>
              <p className="mt-2 font-[Manrope] text-4xl font-bold tracking-tight text-slate-900">16:24:15</p>
              <p className="mt-2 text-sm text-slate-500">Thursday, 10:30 AM IST</p>
            </div>
            <div className="space-y-4">
              <ProgressBar label="Problem Solving" value={92} helper="Excellent decomposition speed" />
              <ProgressBar label="System Design" value={84} helper="Focus on trade-off articulation" />
              <ProgressBar label="Communication" value={88} helper="Improve concise summaries" />
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Next actions" subtitle="Priority checklist for this cycle">
          <ul className="space-y-3 text-sm">
            {checklist.map((item) => (
              <li key={item.task}>
                <button
                  onClick={() => setChecklist((prev) => prev.map((entry) => (entry.task === item.task ? { ...entry, done: !entry.done } : entry)))}
                  className="flex w-full items-center gap-2.5 rounded-xl px-2 py-1.5 text-left text-slate-700 transition hover:bg-[#f7f9fb]"
                >
                  {item.done ? <CheckCircle2 className="h-4 w-4 text-emerald-600" /> : <Circle className="h-4 w-4 text-slate-300" />}
                  {item.task}
                </button>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="AI recommendations" subtitle="Personalized suggestions from performance engine">
          <div className="space-y-3 text-sm text-slate-600">
            <p className="rounded-2xl bg-[#f2f4f6] p-3"><Sparkles className="mr-2 inline h-4 w-4 text-[#004ac6]" />Lead with architecture constraints before implementation depth.</p>
            <p className="rounded-2xl bg-[#f2f4f6] p-3"><BrainCircuit className="mr-2 inline h-4 w-4 text-[#004ac6]" />Use one real production incident for behavioral story depth.</p>
            <p className="rounded-2xl bg-[#f2f4f6] p-3"><Target className="mr-2 inline h-4 w-4 text-[#004ac6]" />Practice a trade-off matrix for caching and consistency discussions.</p>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Recruiter notes" subtitle="Latest feedback from the hiring team" className="xl:col-span-2">
          <div className="space-y-3 text-sm text-slate-600">
            <p className="rounded-2xl bg-[#f2f4f6] p-4"><FilePenLine className="mr-2 inline h-4 w-4 text-slate-500" />Candidate demonstrates strong ownership; probe deeper on ambiguity handling during architecture reviews.</p>
            <p className="rounded-2xl bg-[#f2f4f6] p-4"><CalendarClock className="mr-2 inline h-4 w-4 text-slate-500" />Panel priorities were updated to emphasize scalability and communication calibration.</p>
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
