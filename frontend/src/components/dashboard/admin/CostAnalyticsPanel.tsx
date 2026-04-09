import React from 'react';
import type { EvaluationDashboardResponse } from '../../../types';

interface CostAnalyticsPanelProps {
  evaluationData?: EvaluationDashboardResponse | null;
}

export const CostAnalyticsPanel: React.FC<CostAnalyticsPanelProps> = ({ evaluationData }) => {
  const d = evaluationData;

  return (
    <div className="bg-surface-container-highest/30 rounded-xl p-6">
      <h5 className="font-headline font-bold text-sm mb-4 text-slate-900 dark:text-slate-800">Cost Analytics</h5>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <span className="text-xs text-outline">Daily AI Spend</span>
          <span className="text-sm font-bold font-headline">{d ? `$${d.cost.daily_ai_spend.toFixed(2)}` : '—'}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-outline">Avg Cost/Request</span>
          <span className="text-sm font-bold font-headline text-primary">{d ? `$${d.cost.average_cost_per_request.toFixed(4)}` : '—'}</span>
        </div>
        {/* Model cost breakdown */}
        {d?.cost.cost_by_model && d.cost.cost_by_model.length > 0 && (
          <div className="space-y-2 mt-2">
            {d.cost.cost_by_model.map((m) => (
              <div key={m.model} className="flex items-center justify-between text-[10px]">
                <span className="text-on-surface-variant truncate max-w-[60%]">{m.model}</span>
                <span className="font-bold">${m.cost.toFixed(3)}</span>
              </div>
            ))}
          </div>
        )}
        {/* Mini bar chart fallback */}
        <div className="h-16 w-full mt-1 flex items-end gap-1">
          {[2, 4, 3, 6, 8].map((h, i) => (
            <div
              key={i}
              className="flex-1 rounded-t-sm"
              style={{ height: `${h * 10}%`, backgroundColor: `rgba(0, 74, 198, ${0.3 + i * 0.15})` }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
};
