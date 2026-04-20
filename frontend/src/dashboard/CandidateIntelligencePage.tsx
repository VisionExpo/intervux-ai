import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, CalendarClock, CheckCircle2, Circle, FilePenLine, Sparkles, Target } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { ProgressBar } from "../components/ui/ProgressBar";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "./DashboardShared.module.css";

import { useCandidateDashboard } from "../hooks/useDashboard";

export default function CandidateIntelligencePage() {
  const { data, loading, error } = useCandidateDashboard();
  const [checklist, setChecklist] = useState<{ task: string; done: boolean }[]>([]);

  usePageMeta("Candidate Intelligence Dashboard | Intervux AI", "AI-powered candidate command center with next actions, interview countdown, and intelligence recommendations.");

  useEffect(() => {
    if (data?.checklist) {
      setChecklist(data.checklist);
    } else {
      // Temporary fallback until backend is fully wired for this endpoint
      setChecklist([
        { task: "Review distributing systems notes", done: true },
        { task: "Practice STAR format responses", done: false },
        { task: "Submit final availability preference", done: false },
        { task: "Upload portfolio examples", done: true },
      ]);
    }
  }, [data]);

  if (loading) return <DashboardSkeleton />;
  if (error && !data) return <div style={{ padding: '2rem', color: 'red' }}>Error loading dashboard: {error}</div>;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
      <section className="bg-gradient-to-br from-[var(--accent-indigo)] to-[var(--accent-ocean)] rounded-[var(--radius-lg)] p-8 text-white shadow-[var(--shadow-lg)]">
        <p className="text-sm opacity-90">Welcome back, Vishal</p>
        <h1 className="mt-1 font-heading text-4xl md:text-5xl font-bold tracking-tight leading-tight">
          Your candidate intelligence workspace
        </h1>
        <p className="mt-3 text-sm max-w-2xl opacity-90">
          Intervux AI refreshed your interview strategy using recruiter calibration trends and recent performance telemetry.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Next Interview" value="16h 24m" change="Tomorrow at 10:30 AM" />
        <StatCard label="Readiness Score" value="89" change="+6 pts this week" />
        <StatCard label="AI Confidence" value="93%" change="Strong trajectory" />
        <StatCard label="Task Completion" value={`${Math.round((checklist.filter((c) => c.done).length / Math.max(1, checklist.length)) * 100)}%`} change="Checklist progress" trend="down" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Next interview countdown" subtitle="Senior Backend Engineer • Technical panel" className={sharedStyles.bentoColSpan2}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-6 border border-[var(--border-glass)]">
              <p className="text-xs uppercase tracking-widest text-[var(--text-secondary)]">Countdown</p>
              <p className="mt-2 font-heading text-4xl font-bold text-[var(--text-primary)] leading-none">
                16:24:15
              </p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Thursday, 10:30 AM IST</p>
            </div>
            <div className="flex flex-col gap-4 justify-center">
              <ProgressBar label="Problem Solving" value={92} helper="Excellent decomposition speed" />
              <ProgressBar label="System Design" value={84} helper="Focus on trade-off articulation" />
              <ProgressBar label="Communication" value={88} helper="Improve concise summaries" />
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Next actions" subtitle="Priority checklist for this cycle">
          <ul className="list-none p-0 flex flex-col gap-2">
            {checklist.map((item) => (
              <li key={item.task}>
                <button
                  onClick={() => setChecklist((prev) => prev.map((entry) => (entry.task === item.task ? { ...entry, done: !entry.done } : entry)))}
                  className="flex w-full items-center gap-3 rounded-[var(--radius-sm)] px-3 py-2 bg-transparent border-none text-left text-[var(--text-primary)] cursor-pointer transition-colors duration-200 hover:bg-[var(--surface-glass-light)] focus:bg-[var(--surface-glass-light)]"
                >
                  {item.done ? <CheckCircle2 size={16} className="text-[var(--accent-success-glow)]" /> : <Circle size={16} className="text-[var(--text-tertiary)]" />}
                  <span className="text-sm">{item.task}</span>
                </button>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="AI recommendations" subtitle="Personalized suggestions from performance engine">
          <div className="flex flex-col gap-3">
            <p className="flex items-center gap-2 bg-[var(--surface-glass-light)] p-3 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)]">
              <Sparkles size={16} className="text-[var(--accent-indigo)] shrink-0" />
              <span>Lead with architecture constraints before implementation depth.</span>
            </p>
            <p className="flex items-center gap-2 bg-[var(--surface-glass-light)] p-3 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)]">
              <BrainCircuit size={16} className="text-[var(--accent-indigo)] shrink-0" />
              <span>Use one real production incident for behavioral story depth.</span>
            </p>
            <p className="flex items-center gap-2 bg-[var(--surface-glass-light)] p-3 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)]">
              <Target size={16} className="text-[var(--accent-indigo)] shrink-0" />
              <span>Practice a trade-off matrix for caching and consistency discussions.</span>
            </p>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Recruiter notes" subtitle="Latest feedback from the hiring team" className={sharedStyles.bentoColSpan2}>
          <div className="flex flex-col gap-3">
            <p className="flex items-start gap-2 bg-[var(--surface-glass-light)] p-4 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)] border border-[var(--border-glass)]">
              <FilePenLine size={16} className="text-[var(--text-tertiary)] shrink-0 mt-0.5" />
              <span>Candidate demonstrates strong ownership; probe deeper on ambiguity handling during architecture reviews.</span>
            </p>
            <p className="flex items-start gap-2 bg-[var(--surface-glass-light)] p-4 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)] border border-[var(--border-glass)]">
              <CalendarClock size={16} className="text-[var(--text-tertiary)] shrink-0 mt-0.5" />
              <span>Panel priorities were updated to emphasize scalability and communication calibration.</span>
            </p>
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
