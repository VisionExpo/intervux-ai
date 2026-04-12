import type { ReactNode } from "react";
import { motion } from "framer-motion";
import styles from "../../dashboard/DashboardShared.module.css";

interface SurfaceCardProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function SurfaceCard({ title, subtitle, action, children, className = "" }: SurfaceCardProps) {
  return (
    <motion.section
      className={`${styles.cardGlass} ${className}`}
    >
      {(title || subtitle || action) && (
        <header className="mb-5 flex items-start justify-between gap-3">
          <div>
            {title ? <h3 className={styles.pageTitle} style={{ fontSize: '1.25rem' }}>{title}</h3> : null}
            {subtitle ? <p className={styles.pageSubtitle}>{subtitle}</p> : null}
          </div>
          {action}
        </header>
      )}
      {children}
    </motion.section>
  );
}
