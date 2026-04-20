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
    <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
      <section className="bg-[var(--surface-glass-heavy)] rounded-[var(--radius-lg)] p-8 border border-[var(--border-glass)] shadow-[var(--shadow-sm)]">
        <p className="text-sm text-[var(--text-secondary)]">Recruiter Workspace</p>
        <h1 className="mt-1 font-heading text-3xl font-bold text-[var(--text-primary)] tracking-tight leading-tight">
          Interview operations
        </h1>
      </section>

      <SurfaceCard title="Interview queue" subtitle="This route is now active and ready for interview queue integration.">
        <p className="m-0 text-[15px] text-[var(--text-secondary)] flex items-center gap-2">
          <CalendarCheck2 size={16} />
          This screen is live to prevent dead navigation. We can now connect it to interview APIs and scheduling widgets.
        </p>
      </SurfaceCard>
    </motion.div>
  );
}
