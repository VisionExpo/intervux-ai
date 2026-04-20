import { memo } from "react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import styles from "../../dashboard/DashboardShared.module.css";

interface StatCardProps {
  label: string;
  value: string;
  change: string;
  trend?: "up" | "down";
}

export const StatCard = memo(function StatCard({ label, value, change, trend = "up" }: StatCardProps) {
  const positive = trend === "up";

  return (
    <motion.div 
      whileHover={{ y: -4, scale: 1.02 }}
      className={`${styles.metricTile} group relative overflow-hidden`}
    >
      <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      <p className={styles.metricLabel}>{label}</p>
      <p className={styles.metricValue}>{value}</p>
      <p 
        className={positive ? styles.badgeSuccess : styles.badgeWarning} 
        style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '0.25rem', 
          width: 'fit-content', 
          marginTop: '0.5rem',
          fontSize: '0.75rem',
          fontWeight: 600
        }}
      >
        {positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
        {change}
      </p>
    </motion.div>
  );
});
