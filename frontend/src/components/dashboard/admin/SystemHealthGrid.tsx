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
  const queueStatus = d?.system_health 
    ? (d.system_health.queue_length > 20 ? 'warn' : 'ok') 
    : 'ok';
    
  const gpuStatus = d?.system_health 
    ? (d.system_health.gpu_memory_allocated_mb > d.system_health.gpu_memory_reserved_mb * 0.95 ? 'down' : 
       d.system_health.gpu_memory_allocated_mb > d.system_health.gpu_memory_reserved_mb * 0.8 ? 'warn' : 'ok') 
    : 'ok';

  const latencyStatus = d?.performance?.latency?.p95 
    ? (d.performance.latency.p95 > 2000 ? 'down' : 
       d.performance.latency.p95 > 1000 ? 'warn' : 'ok') 
    : 'ok';

  const errorStatus = d?.performance?.error_rate !== undefined
    ? (d.performance.error_rate > 0.05 ? 'down' : 
       d.performance.error_rate > 0.01 ? 'warn' : 'ok')
    : 'ok';

  const services: Service[] = [
    { icon: 'dns', label: 'API Gateway', status: latencyStatus },
    { icon: 'database', label: 'Postgres', status: 'ok' }, // Typically binary ok/down, keep simple
    { icon: 'bolt', label: 'Redis Cache', status: queueStatus },
    { icon: 'psychology', label: 'LLM Service', status: gpuStatus, highlighted: true },
    { icon: 'settings_voice', label: 'Voice Engine', status: errorStatus },
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
            className={`bg-surface-container-lowest p-4 rounded-xl flex items-center justify-between transition-all hover:shadow-md
              ${highlighted ? 'border-2 border-primary-fixed' : 'border border-outline-variant/10'} 
              ${status === 'down' ? 'opacity-50 ring-1 ring-error/20 bg-error/5' : ''}
              ${status === 'warn' ? 'ring-1 ring-tertiary/20 bg-tertiary/5' : ''}
            `}
          >
            <div className="flex items-center gap-2">
              <span className={`material-symbols-outlined text-xl ${STATUS_ICON[status]}`}>{icon}</span>
              <span className="text-xs font-bold text-slate-900 dark:text-slate-800">{label}</span>
            </div>
            <div className="relative flex items-center justify-center">
               <span className={`w-2 h-2 rounded-full ${STATUS_DOT[status]}`}></span>
               {status === 'warn' && <span className="absolute w-4 h-4 rounded-full border border-tertiary animate-ping opacity-25"></span>}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
