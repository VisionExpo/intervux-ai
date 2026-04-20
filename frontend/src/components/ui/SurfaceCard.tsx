import type { ReactNode } from "react";
import { memo } from "react";
import { motion } from "framer-motion";
import styles from "../../dashboard/DashboardShared.module.css";

interface SurfaceCardProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const SurfaceCard = memo(function SurfaceCard({ title, subtitle, action, children, className = "" }: SurfaceCardProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`${styles.cardGlass} ${className} relative overflow-hidden`}
    >
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      {(title || subtitle || action) && (
        <header className="mb-6 flex items-start justify-between gap-3">
          <div>
            {title ? <h3 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">{title}</h3> : null}
            {subtitle ? <p className="text-sm text-[var(--text-secondary)] mt-1 font-medium">{subtitle}</p> : null}
          </div>
          {action}
        </header>
      )}
      <div className="relative z-10">
        {children}
      </div>
    </motion.section>
  );
});
