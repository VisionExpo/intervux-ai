import React from 'react';
import type { EvaluationDashboardResponse } from '../../../types';

interface SystemHealthGridProps {
  evaluationData?: EvaluationDashboardResponse | null;
}

interface Service {
  icon: string;
  label: string;
  status: 'ok' | 'warn' | 'down';
  highlighted?: boolean;
}

const STATUS_DOT: Record<string, string> = {
  ok: 'bg-primary',
  warn: 'bg-tertiary',
  down: 'bg-slate-400',
};

const STATUS_ICON: Record<string, string> = {
  ok: 'text-primary',
  warn: 'text-tertiary',
  down: 'text-slate-400',
};

export const SystemHealthGrid: React.FC<SystemHealthGridProps> = ({ evaluationData }) => {
  const d = evaluationData;

  // Derive service status from real data when available
  const queueHealthy = d ? d.system_health.queue_length < 50 : true;
  const gpuOk = d ? d.system_health.gpu_memory_allocated_mb < d.system_health.gpu_memory_reserved_mb * 0.9 : true;

  const services: Service[] = [
    { icon: 'dns', label: 'API Gateway', status: 'ok' },
    { icon: 'database', label: 'Postgres', status: 'ok' },
    { icon: 'bolt', label: 'Redis Cache', status: queueHealthy ? 'ok' : 'warn' },
    { icon: 'psychology', label: 'LLM Service', status: gpuOk ? 'ok' : 'warn', highlighted: true },
    { icon: 'settings_voice', label: 'Voice Engine', status: 'ok' },
    { icon: 'hub', label: 'WebSocket', status: d ? 'ok' : 'down' },
  ];

  return (
    <section className="space-y-4 pb-12">
      <div className="flex items-center justify-between">
        <h4 className="font-headline text-lg font-bold text-slate-900 dark:text-slate-800">System Health &amp; Microservices</h4>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
          <span className="text-xs font-bold text-primary">LIVE MONITOR</span>
          {d && (
            <span className="text-[10px] text-slate-400 ml-2">
              {d.system_health.active_interview_sessions} active sessions
            </span>
          )}
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {services.map(({ icon, label, status, highlighted }) => (
          <div
            key={label}
            className={`bg-surface-container-lowest p-4 rounded-xl flex items-center justify-between ${highlighted ? 'border-2 border-primary-fixed' : ''} ${status === 'down' ? 'opacity-50' : ''}`}
          >
            <div className="flex items-center gap-2">
              <span className={`material-symbols-outlined text-xl ${STATUS_ICON[status]}`}>{icon}</span>
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-800">{label}</span>
            </div>
            <span className={`w-2.5 h-2.5 rounded-full ${STATUS_DOT[status]}`}></span>
          </div>
        ))}
      </div>
    </section>
  );
};
