import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Bell, Filter, Search, Sparkles, Star } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { StatCard } from "../components/ui/StatCard";
import { DashboardSkeleton } from "../components/ui/DashboardSkeleton";
import { DataTable, type Column } from "../components/ui/DataTable/DataTable";
import { usePageMeta } from "../hooks/usePageMeta";
import sharedStyles from "./DashboardShared.module.css";

interface Candidate {
  name: string;
  role: string;
  score: number;
  stage: string;
}

import { useRecruiterDashboard } from "../hooks/useDashboard";

const candidateColumns: Column<Candidate>[] = [
  { key: "name", label: "Candidate", sortable: true, render: (row) => <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{row.name}</span> },
  { key: "role", label: "Role", sortable: true },
  { key: "score", label: "AI Score", sortable: true, align: "center", render: (row) => <span className={sharedStyles.badgePrimary}>{row.score}</span> },
  { key: "stage", label: "Stage", sortable: true },
];

export default function RecruiterOperationsPage() {
  const { data, loading, error } = useRecruiterDashboard();
  const [query, setQuery] = useState("");
  const [stageFilter, setStageFilter] = useState("All");

  usePageMeta("Recruiter Dashboard | Intervux AI", "ATS intelligence dashboard with AI candidate ranking, scorecards, and activity stream.");

  const activeCandidates = data?.candidates || [
    { name: "Aisha Rao", role: "Senior Frontend Engineer", score: 95, stage: "Panel" },
    { name: "Mohan Patel", role: "Platform Engineer", score: 92, stage: "System Design" },
    { name: "Elena Cruz", role: "Data Engineer", score: 88, stage: "Recruiter Screen" },
    { name: "Noah Wright", role: "AI Product Manager", score: 84, stage: "Offer Review" },
  ];

  const filteredCandidates = useMemo(
    () =>
      activeCandidates.filter((candidate) => {
        const byQuery = candidate.name.toLowerCase().includes(query.toLowerCase()) || candidate.role.toLowerCase().includes(query.toLowerCase());
        const byStage = stageFilter === "All" || candidate.stage === stageFilter;
        return byQuery && byStage;
      }),
    [query, stageFilter, activeCandidates]
  );

  if (loading) return <DashboardSkeleton />;
  if (error && !data) return <div style={{ padding: '2rem', color: 'red' }}>Error loading dashboard: {error}</div>;

  return (
  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
      <section className="bg-[var(--surface-glass-heavy)] rounded-[var(--radius-lg)] p-8 border border-[var(--border-glass)] shadow-[var(--shadow-sm)]">
        <p className="text-sm text-[var(--text-secondary)]">Recruiter Intelligence Workspace</p>
        <h1 className="mt-1 font-heading text-4xl font-bold text-[var(--text-primary)] tracking-tight leading-tight">
          Modern ATS workflow command center
        </h1>
        <div className="mt-5 flex flex-wrap gap-3">
          <label className="inline-flex items-center gap-2 rounded-[var(--radius-md)] bg-black/20 px-4 py-2 text-sm font-medium text-[var(--text-secondary)] border border-[var(--border-glass)]">
            <Search size={16} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search candidate" className="w-48 bg-transparent text-[var(--text-primary)] border-none outline-none placeholder:text-[var(--text-secondary)]" />
          </label>
          <label className="inline-flex items-center gap-2 rounded-[var(--radius-md)] bg-black/20 px-4 py-2 text-sm font-medium text-[var(--text-secondary)] border border-[var(--border-glass)]">
            <Filter size={16} />
            <select value={stageFilter} onChange={(event) => setStageFilter(event.target.value)} className="bg-transparent text-[var(--text-primary)] border-none outline-none">
              <option value="All" className="text-black">All Stages</option>
              <option value="Recruiter Screen" className="text-black">Recruiter Screen</option>
              <option value="System Design" className="text-black">System Design</option>
              <option value="Panel" className="text-black">Panel</option>
              <option value="Offer Review" className="text-black">Offer Review</option>
            </select>
          </label>
          <button className="inline-flex items-center gap-2 rounded-[var(--radius-md)] bg-[var(--accent-ocean-glow)] px-4 py-2 text-sm font-semibold text-[var(--accent-ocean)] border border-sky-500/30 cursor-pointer transition-colors hover:bg-sky-500/20">
            <Bell size={16} />
            7 notifications
          </button>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Open Roles" value="18" change="4 critical roles" />
        <StatCard label="Active Candidates" value="246" change="+12% WoW" />
        <StatCard label="Avg Time-to-Decision" value="2.4d" change="-14% faster" />
        <StatCard label="Alignment Score" value="94%" change="Across hiring pods" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Pipeline overview" subtitle="Role-based candidate scoring by stage" className={sharedStyles.bentoColSpan2}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {[
              ["Sourced", "72"],
              ["Screening", "49"],
              ["Panel", "31"],
              ["Offer", "11"],
            ].map(([label, value]) => (
              <div key={label} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
                <p className="text-[var(--text-secondary)]">{label}</p>
                <p className="mt-2 font-heading text-3xl font-bold text-[var(--text-primary)]">{value}</p>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard title="AI ranking system" subtitle="Top candidates by weighted fit">
          <ul className="list-none p-0 m-0 flex flex-col gap-3">
            {filteredCandidates.slice(0, 3).map((candidate) => (
              <li key={candidate.name} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
                <p className="text-sm font-semibold text-[var(--text-primary)]">{candidate.name}</p>
                <p className="text-xs text-[var(--text-secondary)]">{candidate.role}</p>
                <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-[var(--accent-indigo-glow)] px-2 py-1 text-xs font-semibold text-[#cedaff] border border-indigo-500/40">
                  <Sparkles size={14} />{candidate.score} fit score
                </span>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <div className={sharedStyles.bentoColSpan2}>
          <DataTable<Candidate>
            columns={candidateColumns}
            data={filteredCandidates}
            rowKey={(row) => row.name}
            title="Candidate list"
            subtitle="Ranked for current role selection"
            emptyText="No candidates match your filters."
          />
        </div>

        <SurfaceCard title="Activity stream" subtitle="Live recruiter and system events">
          <ul className="list-none p-0 m-0 flex flex-col gap-3 text-sm text-[var(--text-secondary)]">
            {["Priya moved Aisha Rao to final panel.", "Model v4.2 recalibrated backend weightage.", "2 candidates flagged for low confidence delta.", "Interview report synced to hiring manager workspace."].map((item) => (
              <li key={item} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-3 border border-[var(--border-glass)]">{item}</li>
            ))}
          </ul>
          <div className="mt-4 bg-[var(--accent-danger-glow)] rounded-[var(--radius-md)] p-3 text-xs font-semibold text-[#fca5a5] border border-rose-600/30 flex items-center gap-1">
            <Star size={14} className="shrink-0" /> Review two low-confidence scorecards before final shortlist.
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
