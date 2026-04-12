import type { ReactNode } from "react";
import { motion } from "framer-motion";

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
      whileHover={{ y: -3 }}
      transition={{ type: "spring", stiffness: 280, damping: 26 }}
      className={`rounded-3xl border border-slate-200 bg-white p-5 shadow-[0_10px_30px_-15px_rgba(15,23,42,0.25)] ${className}`}
    >
      {(title || subtitle || action) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title ? <h3 className="text-base font-semibold text-slate-900">{title}</h3> : null}
            {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
          </div>
          {action}
        </header>
      )}
      {children}
    </motion.section>
  );
}

