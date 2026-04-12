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
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "../dashboard/DashboardShared.module.css";

const confidenceTrend = [
  { day: "Mon", confidence: 91, drift: 4.2 },
  { day: "Tue", confidence: 93, drift: 3.9 },
  { day: "Wed", confidence: 92, drift: 3.2 },
  { day: "Thu", confidence: 95, drift: 2.8 },
  { day: "Fri", confidence: 94, drift: 2.6 },
  { day: "Sat", confidence: 96, drift: 2.1 },
];

export default function AdminCommandCenterPage() {
  usePageMeta("Admin Dashboard | Intervux AI", "Enterprise admin command center with KPI cards, model confidence, system health, and experiment tracking.");

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{
        background: 'var(--surface-glass-heavy)',
        borderRadius: 'var(--radius-lg)',
        padding: '2rem',
        border: '1px solid var(--border-glass)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Admin Command Center</p>
        <h1 style={{ marginTop: '0.25rem', fontFamily: 'var(--font-heading)', fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
          Global intelligence & governance
        </h1>
        <p style={{ marginTop: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Track model confidence, scoring drift, alignment analytics, audit behavior, and experiment impact from one enterprise workspace.
        </p>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        <StatCard label="Hiring Decisions" value="4,812" change="+8.4% this month" />
        <StatCard label="Model Confidence" value="95.1%" change="+1.2pts stability" />
        <StatCard label="Scoring Drift" value="2.1%" change="Within guardrail" />
        <StatCard label="System Uptime" value="99.98%" change="No major incidents" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Model confidence and drift" subtitle="Real-time confidence quality" className={sharedStyles.bentoColSpan2}>
          <div style={{ height: '18rem', width: '100%', marginTop: '1rem' }}>
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
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
            {[
              ["Realtime interview gateway", "Healthy"],
              ["Evaluation workers", "Healthy"],
              ["Queue latency", "Normal"],
              ["Storage replication", "Healthy"],
            ].map(([label, status]) => (
              <li key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--surface-glass-light)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                <span style={{ color: 'var(--text-primary)' }}>{label}</span>
                <span className={sharedStyles.badgePrimary}>{status}</span>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Experiment tracking" subtitle="Active model and rubric experiments">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
            <div style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '1rem', border: '1px solid var(--border-glass)' }}>
              <p style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Exp-204: Calibration weighting</p>
              <p style={{ marginTop: '0.25rem', color: 'var(--text-secondary)' }}>Impact: +3.1 alignment score</p>
            </div>
            <div style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '1rem', border: '1px solid var(--border-glass)' }}>
              <p style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Exp-197: Prompt guardrails</p>
              <p style={{ marginTop: '0.25rem', color: 'var(--text-secondary)' }}>Impact: -1.4 bias variance</p>
            </div>
            <div style={{ background: 'var(--accent-ocean-glow)', borderRadius: 'var(--radius-md)', padding: '1rem', color: '#7dd3fc', fontWeight: 600, border: '1px solid rgba(14, 165, 233, 0.3)' }}>
              2 experiments ready for rollout approval.
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Audit logs" subtitle="Recent governance events" className={sharedStyles.bentoColSpan2}>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {["09:12 - RBAC policy update approved by admin.singh", "09:04 - Confidence threshold changed from 0.88 to 0.9", "08:43 - Recruiter role provisioning for Team Delta", "08:20 - Experiment Exp-204 promoted to staged rollout"].map((item) => (
              <li key={item} style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem', border: '1px solid var(--border-glass)' }}>{item}</li>
            ))}
          </ul>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
