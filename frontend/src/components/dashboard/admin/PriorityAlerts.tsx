import React from 'react';
import type { AlertItem } from '../../../types';

interface PriorityAlertsProps {
  alerts?: AlertItem[];
}

export const PriorityAlerts: React.FC<PriorityAlertsProps> = ({ alerts }) => {
  const displayAlerts = alerts && alerts.length > 0
    ? alerts
    : [
        { severity: 'error', message: 'No active alerts' },
      ];

  const activeCount = alerts?.length ?? 0;

  return (
    <div className="bg-surface-container-lowest rounded-xl p-6 border-l-4 border-error">
      <div className="flex items-center justify-between mb-4">
        <h5 className="font-headline font-bold text-sm text-slate-900 dark:text-slate-800">Priority Alerts</h5>
        <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${activeCount > 0 ? 'bg-error text-on-error' : 'bg-surface-container text-slate-500'}`}>
          {activeCount > 0 ? `${activeCount} ACTIVE` : 'CLEAR'}
        </span>
      </div>
      <div className="space-y-3">
        {displayAlerts.map((alert, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg ${alert.severity === 'error' || alert.severity === 'critical' ? 'bg-error-container/30' : 'bg-surface-container'}`}
          >
            <p className={`text-xs font-bold ${alert.severity === 'error' || alert.severity === 'critical' ? 'text-error' : 'text-on-surface'}`}>
              {alert.severity.toUpperCase()}
            </p>
            <p className="text-[10px] text-on-surface-variant mt-1">{alert.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
