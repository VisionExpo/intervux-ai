import { motion } from "framer-motion";
import { CalendarCheck2 } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { usePageMeta } from "../hooks/usePageMeta";

export default function RecruiterInterviewsPage() {
  usePageMeta(
    "Interviews | Intervux AI",
    "Interview operations workspace for recruiter teams."
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
          Interview operations
        </h1>
      </section>

      <SurfaceCard title="Interview queue" subtitle="This route is now active and ready for interview queue integration.">
        <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <CalendarCheck2 size={16} />
          This screen is live to prevent dead navigation. We can now connect it to interview APIs and scheduling widgets.
        </p>
      </SurfaceCard>
    </motion.div>
  );
}
