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

const candidates: Candidate[] = [
  { name: "Aisha Rao", role: "Senior Frontend Engineer", score: 95, stage: "Panel" },
  { name: "Mohan Patel", role: "Platform Engineer", score: 92, stage: "System Design" },
  { name: "Elena Cruz", role: "Data Engineer", score: 88, stage: "Recruiter Screen" },
  { name: "Noah Wright", role: "AI Product Manager", score: 84, stage: "Offer Review" },
];

const candidateColumns: Column<Candidate>[] = [
  { key: "name", label: "Candidate", sortable: true, render: (row) => <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{row.name}</span> },
  { key: "role", label: "Role", sortable: true },
  { key: "score", label: "AI Score", sortable: true, align: "center", render: (row) => <span className={sharedStyles.badgePrimary}>{row.score}</span> },
  { key: "stage", label: "Stage", sortable: true },
];

export default function RecruiterOperationsPage() {
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [stageFilter, setStageFilter] = useState("All");

  usePageMeta("Recruiter Dashboard | Intervux AI", "ATS intelligence dashboard with AI candidate ranking, scorecards, and activity stream.");

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 700);
    return () => window.clearTimeout(timer);
  }, []);

  const filteredCandidates = useMemo(
    () =>
      candidates.filter((candidate) => {
        const byQuery = candidate.name.toLowerCase().includes(query.toLowerCase()) || candidate.role.toLowerCase().includes(query.toLowerCase());
        const byStage = stageFilter === "All" || candidate.stage === stageFilter;
        return byQuery && byStage;
      }),
    [query, stageFilter]
  );

  if (loading) return <DashboardSkeleton />;

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <section style={{
        background: 'var(--surface-glass-heavy)',
        borderRadius: 'var(--radius-lg)',
        padding: '2rem',
        border: '1px solid var(--border-glass)',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Recruiter Intelligence Workspace</p>
        <h1 style={{ marginTop: '0.25rem', fontFamily: 'var(--font-heading)', fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
          Modern ATS workflow command center
        </h1>
        <div style={{ marginTop: '1.25rem', display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', borderRadius: 'var(--radius-md)', background: 'rgba(0, 0, 0, 0.2)', padding: '0.5rem 1rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)', border: '1px solid var(--border-glass)' }}>
            <Search size={16} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search candidate" style={{ width: '12rem', background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none' }} />
          </label>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', borderRadius: 'var(--radius-md)', background: 'rgba(0, 0, 0, 0.2)', padding: '0.5rem 1rem', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)', border: '1px solid var(--border-glass)' }}>
            <Filter size={16} />
            <select value={stageFilter} onChange={(event) => setStageFilter(event.target.value)} style={{ background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none' }}>
              <option value="All" style={{ color: 'black' }}>All Stages</option>
              <option value="Recruiter Screen" style={{ color: 'black' }}>Recruiter Screen</option>
              <option value="System Design" style={{ color: 'black' }}>System Design</option>
              <option value="Panel" style={{ color: 'black' }}>Panel</option>
              <option value="Offer Review" style={{ color: 'black' }}>Offer Review</option>
            </select>
          </label>
          <button style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', borderRadius: 'var(--radius-md)', background: 'var(--accent-ocean-glow)', padding: '0.5rem 1rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-ocean)', border: '1px solid rgba(14, 165, 233, 0.3)', cursor: 'pointer' }}>
            <Bell size={16} />
            7 notifications
          </button>
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        <StatCard label="Open Roles" value="18" change="4 critical roles" />
        <StatCard label="Active Candidates" value="246" change="+12% WoW" />
        <StatCard label="Avg Time-to-Decision" value="2.4d" change="-14% faster" />
        <StatCard label="Alignment Score" value="94%" change="Across hiring pods" />
      </div>

      <div className={sharedStyles.bentoGrid}>
        <SurfaceCard title="Pipeline overview" subtitle="Role-based candidate scoring by stage" className={sharedStyles.bentoColSpan2}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '1rem', fontSize: '0.875rem' }}>
            {[
              ["Sourced", "72"],
              ["Screening", "49"],
              ["Panel", "31"],
              ["Offer", "11"],
            ].map(([label, value]) => (
              <div key={label} style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '1rem', border: '1px solid var(--border-glass)' }}>
                <p style={{ color: 'var(--text-secondary)' }}>{label}</p>
                <p style={{ marginTop: '0.5rem', fontFamily: 'var(--font-heading)', fontSize: '2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{value}</p>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard title="AI ranking system" subtitle="Top candidates by weighted fit">
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {filteredCandidates.slice(0, 3).map((candidate) => (
              <li key={candidate.name} style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '1rem', border: '1px solid var(--border-glass)' }}>
                <p style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{candidate.name}</p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{candidate.role}</p>
                <p style={{ marginTop: '0.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem', borderRadius: '999px', background: 'var(--accent-indigo-glow)', padding: '0.25rem 0.5rem', fontSize: '0.75rem', fontWeight: 600, color: '#cedaff', border: '1px solid rgba(79, 70, 229, 0.4)' }}>
                  <Sparkles size={14} />{candidate.score} fit score
                </p>
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
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {["Priya moved Aisha Rao to final panel.", "Model v4.2 recalibrated backend weightage.", "2 candidates flagged for low confidence delta.", "Interview report synced to hiring manager workspace."].map((item) => (
              <li key={item} style={{ background: 'var(--surface-glass-light)', borderRadius: 'var(--radius-md)', padding: '0.75rem', border: '1px solid var(--border-glass)' }}>{item}</li>
            ))}
          </ul>
          <div style={{ marginTop: '1rem', background: 'var(--accent-danger-glow)', borderRadius: 'var(--radius-md)', padding: '0.75rem', fontSize: '0.75rem', fontWeight: 600, color: '#fca5a5', border: '1px solid rgba(225, 29, 72, 0.3)' }}>
            <Star style={{ display: 'inline', marginRight: '0.25rem' }} size={14} />Review two low-confidence scorecards before final shortlist.
          </div>
        </SurfaceCard>
      </div>
    </motion.div>
  );
}
