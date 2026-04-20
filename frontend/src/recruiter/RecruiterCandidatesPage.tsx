import { motion } from "framer-motion";
import { Users } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { usePageMeta } from "../hooks/usePageMeta";

export default function RecruiterCandidatesPage() {
  usePageMeta(
    "Candidates | Intervux AI",
    "Candidate roster and shortlist workspace for recruiter teams."
  );

  return (
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} style={{ display: "grid", gap: "1.5rem" }}>
      <section
        style={{
          background: "var(--surface-glass-heavy)",
          borderRadius: "var(--radius-lg)",
          padding: "2rem",
          border: "1px solid var(--border-glass)",
          boxShadow: "var(--shadow-sm)",
        }}
      >
        <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>Recruiter Workspace</p>
        <h1
          style={{
            marginTop: "0.25rem",
            fontFamily: "var(--font-heading)",
            fontSize: "2rem",
            fontWeight: 700,
            color: "var(--text-primary)",
            letterSpacing: "-0.02em",
            lineHeight: 1.1,
          }}
        >
          Candidate roster
        </h1>
      </section>

      <SurfaceCard title="Candidate management" subtitle="This route is now active and ready for candidate list integration.">
        <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Users size={16} />
          This screen is live to prevent dead navigation. We can now connect it to recruiter candidate APIs.
        </p>
      </SurfaceCard>
    </motion.div>
  );
}
