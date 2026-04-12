import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import styles from "../../dashboard/DashboardShared.module.css";

interface StatCardProps {
  label: string;
  value: string;
  change: string;
  trend?: "up" | "down";
}

export function StatCard({ label, value, change, trend = "up" }: StatCardProps) {
  const positive = trend === "up";

  return (
    <div className={styles.metricTile}>
      <p className={styles.metricLabel}>{label}</p>
      <p className={styles.metricValue}>{value}</p>
      <p className={positive ? styles.badgeSuccess : styles.badgeWarning} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', width: 'fit-content', marginTop: '0.5rem' }}>
        {positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
        {change}
      </p>
    </div>
  );
}
