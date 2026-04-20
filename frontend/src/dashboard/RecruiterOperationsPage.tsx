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
  if (error && !data) return <div className="p-8 text-red-500 bg-red-50/50 rounded-lg border border-red-200 glass">Error loading dashboard: {error}</div>;

  const activeCandidates = data?.candidates || [];
  const stats = data?.stats || { openRoles: "0", activeCandidates: "0", avgTime: "0", alignmentScore: "0%" };
  const pipeline = data?.pipeline || [];
  const activityStream = data?.activity_stream || [];

  const filteredCandidates = activeCandidates.filter((candidate) => {
    const byQuery = candidate.name.toLowerCase().includes(query.toLowerCase()) || (candidate.role?.toLowerCase() || "").includes(query.toLowerCase());
    const byStage = stageFilter === "All" || candidate.status === stageFilter;
    return byQuery && byStage;
  });

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
              <option value="invited" className="text-black">Invited</option>
              <option value="in_progress" className="text-black">In Progress</option>
              <option value="completed" className="text-black">Completed</option>
            </select>
          </label>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard label="Open Roles" value={stats.openRoles} change="Live postings" />
        <StatCard label="Active Candidates" value={stats.activeCandidates} change="In pipeline" />
        <StatCard label="Avg Time-to-Decision" value={stats.avgTime} change="Historical average" />
        <StatCard label="Alignment Score" value={stats.alignmentScore} change="Calibration delta" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Pipeline overview" subtitle="Candidate distribution by current state" className={sharedStyles.bentoColSpan2}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {pipeline.map((item) => (
              <div key={item.stage} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
                <p className="text-[var(--text-secondary)]">{item.stage}</p>
                <p className="mt-2 font-heading text-3xl font-bold text-[var(--text-primary)]">{item.count}</p>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard title="Quick ranking" subtitle="Recently added candidates">
          <ul className="list-none p-0 m-0 flex flex-col gap-3">
            {filteredCandidates.slice(0, 3).map((candidate) => (
              <li key={candidate.id} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-4 border border-[var(--border-glass)]">
                <p className="text-sm font-semibold text-[var(--text-primary)]">{candidate.name}</p>
                <p className="text-xs text-[var(--text-secondary)]">{candidate.role}</p>
                <span className="mt-2 inline-flex items-center gap-1 rounded-full bg-[var(--accent-indigo-glow)] px-2 py-1 text-xs font-semibold text-[#cedaff] border border-indigo-500/40">
                  <Sparkles size={14} />{candidate.status}
                </span>
              </li>
            ))}
          </ul>
        </SurfaceCard>
      </div>

      <div className={sharedStyles.bentoGrid}>
        <div className={sharedStyles.bentoColSpan2}>
          <DataTable<any>
            columns={[
              { key: "name", label: "Candidate", sortable: true, render: (row) => <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{row.name}</span> },
              { key: "role", label: "Role", sortable: true },
              { key: "status", label: "Status", sortable: true, render: (row) => <span className={sharedStyles.badgePrimary}>{row.status}</span> },
            ]}
            data={filteredCandidates}
            rowKey={(row) => row.id}
            title="Candidate list"
            subtitle="Live feed from unified database"
            emptyText="No candidates match your filters."
          />
        </div>

        <SurfaceCard title="Activity stream" subtitle="Live system events">
          <ul className="list-none p-0 m-0 flex flex-col gap-3 text-sm text-[var(--text-secondary)]">
            {activityStream.map((item, idx) => (
              <li key={idx} className="bg-[var(--surface-glass-light)] rounded-[var(--radius-md)] p-3 border border-[var(--border-glass)]">{item}</li>
            ))}
            {activityStream.length === 0 && <p className="italic opacity-50">No recent activity detected.</p>}
          </ul>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
