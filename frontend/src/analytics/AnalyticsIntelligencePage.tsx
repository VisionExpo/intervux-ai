import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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
import analyticsReference from "../assets/templates/analytics-reference.png";

const funnelData = [
  { stage: "Applied", value: 540 },
  { stage: "Screened", value: 312 },
  { stage: "Panel", value: 172 },
  { stage: "Offer", value: 64 },
  { stage: "Hired", value: 39 },
];

const trendData = [
  { week: "W1", score: 82, alignment: 88 },
  { week: "W2", score: 84, alignment: 90 },
  { week: "W3", score: 87, alignment: 91 },
  { week: "W4", score: 89, alignment: 93 },
  { week: "W5", score: 90, alignment: 94 },
];

const departmentPerformance = [
  { department: "Engineering", value: 92 },
  { department: "Product", value: 88 },
  { department: "Design", value: 85 },
  { department: "Sales", value: 79 },
];

const heatmap = [
  [0.4, 0.6, 0.7, 0.5, 0.8],
  [0.6, 0.7, 0.8, 0.6, 0.9],
  [0.5, 0.6, 0.9, 0.8, 0.7],
  [0.7, 0.8, 0.9, 0.85, 0.88],
];

export default function AnalyticsIntelligencePage() {
  usePageMeta("Analytics Dashboard | Intervux AI", "Hiring funnel metrics, model trend analytics, bias detection, confidence, and department performance.");

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <section className="rounded-[2rem] border border-slate-200 bg-white px-6 py-6 shadow-sm">
        <p className="text-sm text-slate-500">Intelligence Analytics</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Hiring funnel, model performance, and alignment insights</h1>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Funnel Conversion" value="21.8%" change="+2.6% MoM" />
        <StatCard label="Evaluation Confidence" value="94.2%" change="Stable this week" />
        <StatCard label="Bias Risk Index" value="0.11" change="Below threshold" />
        <StatCard label="Recruiter Alignment" value="93.6%" change="+1.3 pts" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Hiring funnel metrics" subtitle="Stage conversion across pipeline" className="xl:col-span-2">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="stage" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                  {funnelData.map((entry) => (
                    <Cell key={entry.stage} fill="#3b82f6" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Bias detection" subtitle="Protected attribute variance">
          <div className="space-y-3 text-sm text-slate-600">
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 text-emerald-700">Gender variance: 0.04 (Healthy)</div>
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-3 text-emerald-700">Experience variance: 0.07 (Healthy)</div>
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-3 text-amber-700">Education variance: 0.13 (Review)</div>
          </div>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Model score trends" subtitle="Weekly score and alignment trajectory" className="xl:col-span-2">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="week" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="alignment" stroke="#14b8a6" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Evaluation confidence heatmap" subtitle="Department x stage">
          <div className="space-y-2">
            {heatmap.map((row, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-5 gap-2">
                {row.map((value, cellIndex) => (
                  <div
                    key={`${rowIndex}-${cellIndex}`}
                    className="h-10 rounded-lg"
                    style={{ backgroundColor: `rgba(37,99,235,${value})` }}
                    title={`Confidence ${(value * 100).toFixed(0)}%`}
                  />
                ))}
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>

      <SurfaceCard title="Department performance" subtitle="Composite hiring intelligence score">
        <div className="grid gap-3 md:grid-cols-4">
          {departmentPerformance.map((item) => (
            <div key={item.department} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">{item.department}</p>
              <p className="mt-2 text-3xl font-semibold text-slate-900">{item.value}</p>
            </div>
          ))}
        </div>
      </SurfaceCard>

      <SurfaceCard title="Reference Analytics Dashboard" subtitle="Using website template analytics asset">
        <img src={analyticsReference} alt="Analytics template reference" className="w-full rounded-2xl border border-slate-200 object-cover" />
      </SurfaceCard>
    </motion.div>
  );
}

