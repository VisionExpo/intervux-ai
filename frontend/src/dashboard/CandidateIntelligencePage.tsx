import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, CalendarClock, CheckCircle2, Circle, FilePenLine, Sparkles, Target } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { ProgressBar } from "../components/ui/ProgressBar";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "./DashboardShared.module.css";

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
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{
        background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-ocean))',
        borderRadius: 'var(--radius-lg)',
        padding: '2rem',
        color: 'white',
        boxShadow: 'var(--shadow-lg)'
      }}>
        <p style={{ fontSize: '0.875rem', opacity: 0.9 }}>Welcome back, Vishal</p>
        <h1 style={{ marginTop: '0.25rem', fontFamily: 'var(--font-heading)', fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.1 }}>
          Your candidate intelligence workspace
        </h1>
        <p style={{ marginTop: '0.75rem', fontSize: '0.875rem', maxWidth: '42rem', opacity: 0.9 }}>
          Intervux AI refreshed your interview strategy using recruiter calibration trends and recent performance telemetry.
        </p>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        <StatCard label="Next Interview" value="16h 24m" change="Tomorrow at 10:30 AM" />
        <StatCard label="Readiness Score" value="89" change="+6 pts this week" />
        <StatCard label="AI Confidence" value="93%" change="Strong trajectory" />
        <StatCard label="Task Completion" value={`${Math.round((checklist.filter((c) => c.done).length / checklist.length) * 100)}%`} change="Checklist progress" trend="down" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Next interview countdown" subtitle="Senior Backend Engineer • Technical panel" className={sharedStyles.bentoColSpan2}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
            <div style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '1.5rem', border: '1px solid var(--border-glass)' }}>
              <p style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.16em', color: 'var(--text-secondary)' }}>Countdown</p>
              <p style={{ marginTop: '0.5rem', fontFamily: 'var(--font-heading)', fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1 }}>
                16:24:15
              </p>
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Thursday, 10:30 AM IST</p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', justifyContent: 'center' }}>
              <ProgressBar label="Problem Solving" value={92} helper="Excellent decomposition speed" />
              <ProgressBar label="System Design" value={84} helper="Focus on trade-off articulation" />
              <ProgressBar label="Communication" value={88} helper="Improve concise summaries" />
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Next actions" subtitle="Priority checklist for this cycle">
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {checklist.map((item) => (
              <li key={item.task}>
                <button
                  onClick={() => setChecklist((prev) => prev.map((entry) => (entry.task === item.task ? { ...entry, done: !entry.done } : entry)))}
                  style={{
                    display: 'flex', width: '100%', alignItems: 'center', gap: '0.75rem',
                    borderRadius: 'var(--radius-sm)', padding: '0.5rem 0.75rem',
                    background: 'transparent', border: 'none', textAlign: 'left',
                    color: 'var(--text-primary)', cursor: 'pointer', transition: 'var(--transition-fast)'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.background = 'var(--surface-glass-light)'}
                  onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  {item.done ? <CheckCircle2 size={16} color="var(--accent-success-glow)" /> : <Circle size={16} color="var(--text-tertiary)" />}
                  <span style={{ fontSize: '0.875rem' }}>{item.task}</span>
                </button>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="AI recommendations" subtitle="Personalized suggestions from performance engine">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-glass-light)', padding: '0.75rem', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              <Sparkles size={16} color="var(--accent-indigo)" />
              Lead with architecture constraints before implementation depth.
            </p>
            <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-glass-light)', padding: '0.75rem', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              <BrainCircuit size={16} color="var(--accent-indigo)" />
              Use one real production incident for behavioral story depth.
            </p>
            <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-glass-light)', padding: '0.75rem', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              <Target size={16} color="var(--accent-indigo)" />
              Practice a trade-off matrix for caching and consistency discussions.
            </p>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Recruiter notes" subtitle="Latest feedback from the hiring team" className={sharedStyles.bentoColSpan2}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-glass-light)', padding: '1rem', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--text-secondary)', border: '1px solid var(--border-glass)' }}>
              <FilePenLine size={16} color="var(--text-tertiary)" />
              Candidate demonstrates strong ownership; probe deeper on ambiguity handling during architecture reviews.
            </p>
            <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--surface-glass-light)', padding: '1rem', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--text-secondary)', border: '1px solid var(--border-glass)' }}>
              <CalendarClock size={16} color="var(--text-tertiary)" />
              Panel priorities were updated to emphasize scalability and communication calibration.
            </p>
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
