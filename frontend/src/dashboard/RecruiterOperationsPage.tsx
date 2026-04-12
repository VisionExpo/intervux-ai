import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bell, Filter, Search, Sparkles, Star } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { usePageMeta } from "../hooks/usePageMeta";
import recruiterReference from "../assets/templates/recruiter-dashboard-reference.png";

const candidates = [
  { name: "Aisha Rao", role: "Senior Frontend Engineer", score: 95, stage: "Panel" },
  { name: "Mohan Patel", role: "Platform Engineer", score: 92, stage: "System Design" },
  { name: "Elena Cruz", role: "Data Engineer", score: 88, stage: "Recruiter Screen" },
  { name: "Noah Wright", role: "AI Product Manager", score: 84, stage: "Offer Review" },
];

const activity = [
  "Priya moved Aisha Rao to final panel.",
  "Model v4.2 recalibrated backend weightage.",
  "2 candidates flagged for low confidence delta.",
  "Interview report synced to hiring manager workspace.",
];

export default function RecruiterOperationsPage() {
  const [loading, setLoading] = useState(true);

  usePageMeta("Recruiter Dashboard | Intervux AI", "ATS intelligence dashboard with AI candidate ranking, scorecards, and activity stream.");

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 700);
    return () => window.clearTimeout(timer);
  }, []);

  if (loading) return <DashboardSkeleton />;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
      <section className="rounded-[2rem] border border-slate-200 bg-white px-6 py-6 shadow-sm">
        <p className="text-sm text-slate-500">Recruiter Intelligence Workspace</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Modern ATS workflow command center</h1>
        <div className="mt-4 flex flex-wrap gap-2">
          <button className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700"><Search className="h-4 w-4" />Search candidate</button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700"><Filter className="h-4 w-4" />Filters</button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700"><Bell className="h-4 w-4" />7 notifications</button>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Open Roles" value="18" change="4 critical roles" />
        <StatCard label="Active Candidates" value="246" change="+12% week-over-week" />
        <StatCard label="Avg Time-to-Decision" value="2.4d" change="-14% faster" />
        <StatCard label="Alignment Score" value="94%" change="Across hiring pods" />
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Pipeline overview" subtitle="Role-based candidate scoring by stage" className="xl:col-span-2">
          <div className="grid gap-3 md:grid-cols-4 text-sm">
            {[
              ["Sourced", "72"],
              ["Screening", "49"],
              ["Panel", "31"],
              ["Offer", "11"],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-slate-500">{label}</p>
                <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard title="AI ranking system" subtitle="Top candidates by weighted fit">
          <ul className="space-y-3">
            {candidates.slice(0, 3).map((candidate) => (
              <li key={candidate.name} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                <p className="text-sm font-semibold text-slate-900">{candidate.name}</p>
                <p className="text-xs text-slate-500">{candidate.role}</p>
                <p className="mt-2 inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700"><Sparkles className="h-3.5 w-3.5" />{candidate.score} fit score</p>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <SurfaceCard title="Candidate list" subtitle="Ranked for current role selection" className="xl:col-span-2">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[540px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500">
                  <th className="pb-2 font-medium">Candidate</th>
                  <th className="pb-2 font-medium">Role</th>
                  <th className="pb-2 font-medium">AI Score</th>
                  <th className="pb-2 font-medium">Stage</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate) => (
                  <tr key={candidate.name} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                    <td className="py-3 font-semibold text-slate-900">{candidate.name}</td>
                    <td className="py-3 text-slate-600">{candidate.role}</td>
                    <td className="py-3"><span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700">{candidate.score}</span></td>
                    <td className="py-3 text-slate-600">{candidate.stage}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </SurfaceCard>

        <SurfaceCard title="Activity stream" subtitle="Live recruiter and system events">
          <ul className="space-y-3 text-sm text-slate-600">
            {activity.map((item) => (
              <li key={item} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">{item}</li>
            ))}
          </ul>
          <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-3 text-xs font-semibold text-amber-700">
            <Star className="mr-1 inline h-3.5 w-3.5" />
            Review two low-confidence scorecards before final shortlist.
          </div>
        </SurfaceCard>
      </div>

      <SurfaceCard title="Reference ATS Dashboard" subtitle="Using website template recruiter dashboard asset">
        <img src={recruiterReference} alt="Recruiter dashboard template reference" className="w-full rounded-2xl border border-slate-200 object-cover" />
      </SurfaceCard>
    </motion.div>
  );
}

