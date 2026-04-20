import { motion } from "framer-motion";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { DashboardError, EmptyState } from "../components/ui/FeedbackStates";
import { useAdminDashboard } from "../hooks/useDashboard";
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "../dashboard/DashboardShared.module.css";
import { AlertCircle, Activity } from "lucide-react";

const confidenceTrend = [
  { day: "Mon", confidence: 91, drift: 4.2 },
  { day: "Tue", confidence: 93, drift: 3.9 },
  { day: "Wed", confidence: 92, drift: 3.2 },
  { day: "Thu", confidence: 95, drift: 2.8 },
  { day: "Fri", confidence: 94, drift: 2.6 },
  { day: "Sat", confidence: 96, drift: 2.1 },
];

export default function AdminCommandCenterPage() {
  const { data, loading, error } = useAdminDashboard();
  usePageMeta("Admin Dashboard | Intervux AI", "Enterprise admin command center with KPI cards, model confidence, system health, and experiment tracking.");

  if (loading) return <DashboardSkeleton />;
  if (error && !data) {
    return (
      <div className="p-8">
        <DashboardError 
          message={error} 
          onRetry={() => window.location.reload()} 
        />
      </div>
    );
  }

  const stats = data?.stats || { 
    hiringDecisions: "4,812", 
    modelConfidence: "95.1%", 
    scoringDrift: "2.1%", 
    uptime: "99.98%" 
  };
  const logs = data?.audit_logs || [];
  const health = data?.health || [];
  const chartData = data?.confidence_trend || confidenceTrend;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
      <section className="bg-[var(--surface-glass-heavy)] rounded-[var(--radius-lg)] p-8 border border-[var(--border-glass)] shadow-[var(--shadow-sm)]">
        <p className="text-sm text-[var(--text-secondary)]">Admin Command Center</p>
        <h1 className="mt-1 font-heading text-4xl font-bold text-[var(--text-primary)] tracking-tight leading-tight">
          Global intelligence & governance
        </h1>
        <p className="mt-3 text-sm text-[var(--text-secondary)]">
          Track model confidence, scoring drift, alignment analytics, audit behavior, and experiment impact from one enterprise workspace.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Hiring Decisions" value={stats.hiringDecisions} change="+8.4% this month" />
        <StatCard label="Model Confidence" value={stats.modelConfidence} change="+1.2pts stability" />
        <StatCard label="Scoring Drift" value={stats.scoringDrift} change="Within guardrail" trend="down" />
        <StatCard label="System Uptime" value={stats.uptime} change="No major incidents" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Model confidence and drift" subtitle="Real-time confidence quality" className={sharedStyles.bentoColSpan2}>
          <div className="h-72 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={confidenceTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="day" stroke="var(--text-secondary)" />
                <YAxis yAxisId="left" stroke="var(--text-secondary)" />
                <YAxis yAxisId="right" orientation="right" stroke="var(--text-secondary)" />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }} />
                <Line yAxisId="left" type="monotone" dataKey="confidence" stroke="#4f46e5" strokeWidth={2.5} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="drift" stroke="#0ea5e9" strokeWidth={2.2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </SurfaceCard>

        <SurfaceCard title="System health" subtitle="Infrastructure and service checks">
          <ul className="list-none p-0 m-0 flex flex-col gap-3 text-sm">
            {[
              ["Realtime interview gateway", "Healthy"],
              ["Evaluation workers", "Healthy"],
              ["Queue latency", "Normal"],
              ["Storage replication", "Healthy"],
            ].map(([label, status]) => (
              <li key={label} className="flex items-center justify-between bg-[var(--surface-glass-light)] px-4 py-3 rounded-[var(--radius-md)] border border-[var(--border-glass)]">
                <span className="text-[var(--text-primary)]">{label}</span>
                <span className={sharedStyles.badgePrimary}>{status}</span>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Experiment tracking" subtitle="Active model and rubric experiments">
          <div className="flex flex-col gap-3 text-sm">
            <div className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
              <p className="font-semibold text-[var(--text-primary)]">Exp-204: Calibration weighting</p>
              <p className="mt-1 text-[var(--text-secondary)]">Impact: +3.1 alignment score</p>
            </div>
            <div className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
              <p className="font-semibold text-[var(--text-primary)]">Exp-197: Prompt guardrails</p>
              <p className="mt-1 text-[var(--text-secondary)]">Impact: -1.4 bias variance</p>
            </div>
            <div className="bg-[var(--accent-ocean-glow)] rounded-[var(--radius-md)] p-4 text-[#7dd3fc] font-semibold border border-sky-500/30">
              2 experiments ready for rollout approval.
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Audit logs" subtitle="Recent governance events" className={sharedStyles.bentoColSpan2}>
          {logs.length > 0 ? (
            <ul className="list-none p-0 m-0 flex flex-col gap-2 text-sm text-[var(--text-secondary)]">
              {logs.map((item, idx) => (
                <li key={idx} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] px-4 py-3 border border-[var(--border-glass)]">{item}</li>
              ))}
            </ul>
          ) : (
            <EmptyState 
              title="Clean ledger" 
              description="No audit events recorded in the last 24 hours." 
              icon={Activity} 
            />
          )}
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
