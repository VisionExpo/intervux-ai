import React from 'react';
import type { EvaluationDashboardResponse } from '../../../types';
import { formatCurrency, formatPercent } from '../../../hooks/useDashboardApi';

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
      label: 'AI Inference Precision',
      value: d?.model_quality ? formatPercent(d.model_quality.accuracy) : '94.0%',
      trend: d?.model_quality ? `Consistency: ${formatPercent(d.model_quality.consistency_score)}` : 'Target: 95%+',
      trendColor: 'text-primary',
      accent: true,
    },
    {
      label: 'Global Interviews',
      value: d?.system_health ? `${d.system_health.active_interview_sessions.toLocaleString()}` : '—',
      trend: d?.interview_metrics ? `${formatPercent(d.interview_metrics.candidate_success_rate)} success` : '',
      trendColor: 'text-tertiary',
    },
    {
      label: 'Active LLM Nodes',
      value: d?.system_health ? `${d.system_health.active_interview_sessions}` : '24',
      trend: d?.system_health ? `Queue: ${d.system_health.queue_length}` : 'Stable',
      trendColor: 'text-tertiary',
    },
    {
      label: 'System Error Rate',
      value: d?.performance ? formatPercent(d.performance.error_rate) : '0.05%',
      bar: d?.performance ? Math.min(d.performance.error_rate * 1000, 100) : 5,
    },
    {
      label: 'Latency (p95)',
      value: d?.performance?.latency ? `${d.performance.latency.p95.toFixed(0)}ms` : '1,200ms',
      trend: d?.performance?.latency ? `p99: ${d.performance.latency.p99.toFixed(0)}ms` : '',
      trendColor: 'text-primary',
    },
    {
      label: 'Cloud Infrastructure Spend',
      value: d?.cost ? formatCurrency(d.cost.daily_ai_spend) : '$145.50',
      trend: d?.cost ? `Avg: $${d.cost.average_cost_per_request.toFixed(3)}/req` : '',
      trendColor: 'text-primary',
    },
  ];

  return (
    <section className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
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
