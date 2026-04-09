import React from 'react';
import type { EvaluationDashboardResponse } from '../../../types';

interface AdminKPIRowProps {
  evaluationData?: EvaluationDashboardResponse | null;
}

interface KPI {
  label: string;
  value: string;
  trend?: string;
  trendColor?: string;
  accent?: boolean;
  bar?: number;
}

export const AdminKPIRow: React.FC<AdminKPIRowProps> = ({ evaluationData }) => {
  const d = evaluationData;

  const kpis: KPI[] = [
    {
      label: 'Total Interviews',
      value: d?.interview_metrics ? `${d.system_health.active_interview_sessions.toLocaleString()}` : '—',
      trend: d ? `${d.interview_metrics.candidate_success_rate.toFixed(0)}% success` : '',
      trendColor: 'text-primary',
      accent: true,
    },
    {
      label: 'Active Sessions',
      value: d ? `${d.system_health.active_interview_sessions}` : '—',
      trend: d ? `Queue: ${d.system_health.queue_length}` : 'Stable',
      trendColor: 'text-tertiary',
    },
    {
      label: 'AI Accuracy',
      value: d ? `${(d.model_quality.accuracy * 100).toFixed(1)}%` : '—',
      trend: d ? `Hallucination: ${(d.model_quality.hallucination_rate * 100).toFixed(1)}%` : '',
      trendColor: 'text-primary',
    },
    {
      label: 'Error Rate',
      value: d ? `${(d.performance.error_rate * 100).toFixed(2)}%` : '—',
      bar: d ? Math.min(d.performance.error_rate * 1000, 100) : 0,
    },
    {
      label: 'Latency (p95)',
      value: d ? `${d.performance.latency.p95.toFixed(0)}ms` : '—',
      trend: d ? `p99: ${d.performance.latency.p99.toFixed(0)}ms` : '',
      trendColor: 'text-primary',
    },
    {
      label: 'Daily AI Spend',
      value: d ? `$${d.cost.daily_ai_spend.toFixed(2)}` : '—',
      trend: d ? `Avg: $${d.cost.average_cost_per_request.toFixed(3)}/req` : '',
      trendColor: 'text-primary',
    },
  ];

  return (
    <section className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
      {kpis.map(({ label, value, trend, trendColor, accent, bar }) => (
        <div
          key={label}
          className={`bg-surface-container-lowest p-6 rounded-xl ${accent ? 'border-l-4 border-primary-container' : ''}`}
        >
          <p className="text-xs font-semibold text-outline tracking-wider uppercase mb-2">{label}</p>
          <h3 className="text-2xl font-bold font-headline">{value}</h3>
          {trend && (
            <p className={`text-xs font-bold mt-1 ${trendColor ?? 'text-outline'}`}>{trend}</p>
          )}
          {bar !== undefined && bar > 0 && (
            <div className="w-full bg-surface-container h-1 mt-3 rounded-full overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: `${bar}%` }}></div>
            </div>
          )}
        </div>
      ))}
    </section>
  );
};
