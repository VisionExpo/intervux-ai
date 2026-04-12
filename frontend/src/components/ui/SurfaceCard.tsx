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
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 260, damping: 24 }}
      className={`rounded-3xl bg-white p-6 shadow-[0_24px_48px_-36px_rgba(15,23,42,0.35)] ${className}`}
    >
      {(title || subtitle || action) && (
        <header className="mb-5 flex items-start justify-between gap-3">
          <div>
            {title ? <h3 className="font-[Manrope] text-lg font-semibold tracking-tight text-slate-900">{title}</h3> : null}
            {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
          </div>
          {action}
        </header>
      )}
      {children}
    </motion.section>
  );
}
