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
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <section className="rounded-[2rem] bg-white px-6 py-6 shadow-sm">
        <p className="text-sm text-slate-500">Admin Command Center</p>
        <h1 className="mt-1 font-[Manrope] text-3xl font-bold tracking-tight text-slate-900">Global intelligence and governance controls</h1>
        <p className="mt-2 text-sm text-slate-600">Track model confidence, scoring drift, alignment analytics, audit behavior, and experiment impact from one enterprise workspace.</p>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Hiring Decisions" value="4,812" change="+8.4% this month" />
        <StatCard label="Model Confidence" value="95.1%" change="+1.2pts stability" />
        <StatCard label="Scoring Drift" value="2.1%" change="Within guardrail" />
        <StatCard label="System Uptime" value="99.98%" change="No major incidents" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Model confidence and drift" subtitle="Real-time confidence quality" className="xl:col-span-2">
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={confidenceTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="day" stroke="#94a3b8" />
                <YAxis yAxisId="left" stroke="#94a3b8" />
                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" />
                <Tooltip />
                <Line yAxisId="left" type="monotone" dataKey="confidence" stroke="#004ac6" strokeWidth={2.5} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="drift" stroke="#943700" strokeWidth={2.2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </SurfaceCard>

        <SurfaceCard title="System health" subtitle="Infrastructure and service checks">
          <ul className="space-y-3 text-sm">
            {[
              ["Realtime interview gateway", "Healthy"],
              ["Evaluation workers", "Healthy"],
              ["Queue latency", "Normal"],
              ["Storage replication", "Healthy"],
            ].map(([label, status]) => (
              <li key={label} className="flex items-center justify-between rounded-2xl bg-[#f2f4f6] px-3 py-2.5">
                <span className="text-slate-700">{label}</span>
                <span className="rounded-full bg-[#dbe1ff] px-2 py-1 text-xs font-semibold text-[#003ea8]">{status}</span>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Experiment tracking" subtitle="Active model and rubric experiments">
          <div className="space-y-3 text-sm">
            <div className="rounded-2xl bg-[#f2f4f6] p-3">
              <p className="font-semibold text-slate-900">Exp-204: Calibration weighting</p>
              <p className="text-slate-500">Impact: +3.1 alignment score</p>
            </div>
            <div className="rounded-2xl bg-[#f2f4f6] p-3">
              <p className="font-semibold text-slate-900">Exp-197: Prompt guardrails</p>
              <p className="text-slate-500">Impact: -1.4 bias variance</p>
            </div>
            <div className="rounded-2xl bg-[#dbe1ff] p-3 text-[#003ea8]">2 experiments ready for rollout approval.</div>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Audit logs" subtitle="Recent governance events" className="xl:col-span-2">
          <ul className="space-y-2 text-sm text-slate-600">
            {["09:12 - RBAC policy update approved by admin.singh", "09:04 - Confidence threshold changed from 0.88 to 0.9", "08:43 - Recruiter role provisioning for Team Delta", "08:20 - Experiment Exp-204 promoted to staged rollout"].map((item) => (
              <li key={item} className="rounded-2xl bg-[#f2f4f6] p-3">{item}</li>
            ))}
          </ul>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
