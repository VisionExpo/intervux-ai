import { motion } from "framer-motion";
import { BrainCircuit, CalendarClock, CheckCircle2, FilePenLine, Sparkles } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { ProgressBar } from "../components/ui/ProgressBar";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "./DashboardShared.module.css";

import { useCandidateDashboard } from "../hooks/useDashboard";

export default function CandidateIntelligencePage() {
  const { data, loading, error } = useCandidateDashboard();
  usePageMeta("Candidate Intelligence Dashboard | Intervux AI", "AI-powered candidate command center with next actions, interview countdown, and intelligence recommendations.");

  if (loading) return <DashboardSkeleton />;
  if (error && !data) return <div className="p-8 text-red-500 bg-red-50/50 rounded-lg border border-red-200 glass">Error loading dashboard: {error}</div>;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
      <section className="bg-gradient-to-br from-[var(--accent-indigo)] to-[var(--accent-ocean)] rounded-[var(--radius-lg)] p-8 text-white shadow-[var(--shadow-lg)]">
        <p className="text-sm opacity-90">Welcome back</p>
        <h1 className="mt-1 font-heading text-4xl md:text-5xl font-bold tracking-tight leading-tight">
          Your Intelligence Workspace
        </h1>
        <p className="mt-3 text-sm max-w-2xl opacity-90">
          AI insights generated from your profile and resume data.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Profile Readiness" value={`${Math.round(data?.profile_score ?? 0)}%`} change="Overall visibility" />
        <StatCard label="Resume Score" value={`${Math.round(data?.resume_score ?? 0)}%`} change="Content quality" />
        <StatCard label="Avg Interview Score" value={`${Math.round(data?.mock_interview_score ?? 0)}%`} change="Based on last sessions" />
        <StatCard label="Mock Credits" value={data?.mock_interviews_remaining?.toString() ?? "0"} change="Remaining interviews" trend={ (data?.mock_interviews_remaining ?? 0) < 1 ? "down" : "up"} />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Quick stats" subtitle="Your performance telemetry" className={sharedStyles.bentoColSpan2}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-6 border border-[var(--border-glass)]">
              <p className="text-xs uppercase tracking-widest text-[var(--text-secondary)]">Profile Strength</p>
              <p className="mt-2 font-heading text-4xl font-bold text-[var(--text-primary)] leading-none">
                {Math.round(data?.profile_score ?? 0)}
              </p>
              <p className="mt-2 text-sm text-[var(--text-secondary)]">Recruiter visibility index</p>
            </div>
            <div className="flex flex-col gap-4 justify-center">
              <ProgressBar label="Resume Alignment" value={data?.resume_score ?? 0} helper="Based on AI parsing" />
              <ProgressBar label="Interview Performance" value={data?.mock_interview_score ?? 0} helper="Personal trajectory" />
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Recent activity" subtitle="Historical audit logs">
          <ul className="list-none p-0 flex flex-col gap-2">
            {(data?.recent_activity ?? []).length > 0 ? (
              data?.recent_activity.map((activity, idx) => (
                <li key={idx} className="flex items-center gap-3 rounded-[var(--radius-sm)] px-3 py-2 bg-[var(--surface-glass-light)] text-[var(--text-primary)] border border-[var(--border-glass)]">
                  <CheckCircle2 size={16} className="text-[var(--accent-success-glow)] shrink-0" />
                  <span className="text-sm truncate">{activity}</span>
                </li>
              ))
            ) : (
                <li className="text-sm text-[var(--text-secondary)] p-4 text-center italic">No recent activity detected.</li>
            )}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="AI recommendations" subtitle="Personalized suggestions">
          <div className="flex flex-col gap-3">
            <p className="flex items-center gap-2 bg-[var(--surface-glass-light)] p-3 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)]">
              <Sparkles size={16} className="text-[var(--accent-indigo)] shrink-0" />
              <span>Upload a new resume to refresh your AI performance score.</span>
            </p>
            <p className="flex items-center gap-2 bg-[var(--surface-glass-light)] p-3 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)]">
              <BrainCircuit size={16} className="text-[var(--accent-indigo)] shrink-0" />
              <span>Complete a mock interview to unlock behavioral feedback.</span>
            </p>
          </div>
        </SurfaceCard>

        <SurfaceCard title="System insight" subtitle="Candidate-side diagnostic feed" className={sharedStyles.bentoColSpan2}>
          <div className="flex flex-col gap-3">
            <p className="flex items-start gap-2 bg-[var(--surface-glass-light)] p-4 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)] border border-[var(--border-glass)]">
              <FilePenLine size={16} className="text-[var(--text-tertiary)] shrink-0 mt-0.5" />
              <span>Your profile score is used by the matching engine to showcase your skills to recruiters.</span>
            </p>
            <p className="flex items-start gap-2 bg-[var(--surface-glass-light)] p-4 rounded-[var(--radius-md)] text-sm text-[var(--text-secondary)] border border-[var(--border-glass)]">
              <CalendarClock size={16} className="text-[var(--text-tertiary)] shrink-0 mt-0.5" />
              <span>Mock interview credits reset upon purchase of enterprise packs.</span>
            </p>
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
