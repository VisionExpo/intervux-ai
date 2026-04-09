import React from 'react';
import type { EvaluationDashboardResponse } from '../../../types';

interface AIIntelligencePanelProps {
  evaluationData?: EvaluationDashboardResponse | null;
}

export const AIIntelligencePanel: React.FC<AIIntelligencePanelProps> = ({ evaluationData }) => {
  const d = evaluationData;
  const latencyPct = d ? Math.min((d.performance.latency.p50 / 5000) * 100, 100) : 30;

  return (
    <div className="bg-surface-container-low rounded-xl p-6 border-l-2 border-primary-container">
      <h5 className="font-headline font-bold text-sm mb-4 text-slate-900 dark:text-slate-800">AI Intelligence Layer</h5>
      <div className="space-y-5">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-outline">Model Latency (p50)</span>
            <span className="font-bold">{d ? `${d.performance.latency.p50.toFixed(0)}ms` : '—'}</span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded-full overflow-hidden">
            <div className="bg-primary h-full" style={{ width: `${latencyPct}%` }}></div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-[10px] text-outline uppercase tracking-wider">Consistency</p>
            <p className="text-lg font-bold font-headline">{d ? `${(d.model_quality.consistency_score * 100).toFixed(0)}%` : '—'}</p>
          </div>
          <div>
            <p className="text-[10px] text-outline uppercase tracking-wider">Reasoning</p>
            <p className="text-lg font-bold font-headline">{d ? `${(d.model_quality.reasoning_score * 100).toFixed(0)}%` : '—'}</p>
          </div>
        </div>
        <div className="p-3 bg-surface-container-lowest rounded-lg">
          <p className="text-xs font-bold mb-1">Token Usage</p>
          <div className="flex justify-between items-center">
            <span className="text-[10px] text-on-surface-variant">{d ? `${d.token_usage.total_tokens_today.toLocaleString()} tokens today` : '—'}</span>
            <span className="text-[10px] font-bold text-primary">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
