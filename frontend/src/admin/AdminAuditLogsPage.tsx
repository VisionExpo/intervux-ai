import { motion } from "framer-motion";
import { ClipboardList } from "lucide-react";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { usePageMeta } from "../hooks/usePageMeta";

export default function AdminAuditLogsPage() {
  usePageMeta(
    "Audit Logs | Intervux AI",
    "Operational and governance event history for Intervux AI administrators."
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
        <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>Admin Governance</p>
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
          Audit logs
        </h1>
      </section>

      <SurfaceCard title="Governance events" subtitle="This route is now active and ready for audit event integration.">
        <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <ClipboardList size={16} />
          This screen is live to prevent dead navigation. Next step is connecting real audit events.
        </p>
      </SurfaceCard>
    </motion.div>
  );
}
