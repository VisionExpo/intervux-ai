import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

const BARS = [40, 60, 55, 80, 70, 95, 85, 60, 45, 50, 70, 100, 65, 50, 88, 40, 30, 60, 90, 75];

export const ActivityTrendsChart: React.FC = () => {
  return (
    <DashboardCard>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h4 className="font-headline text-lg font-bold text-slate-900 dark:text-slate-800">Platform Activity Trends</h4>
          <p className="text-sm text-outline">Hourly aggregated traffic and engagement volume</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary"></div>
            <span className="text-xs font-medium">Interviews</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-tertiary"></div>
            <span className="text-xs font-medium">Candidates</span>
          </div>
        </div>
      </div>
      <div className="h-64 w-full flex items-end justify-between gap-1">
        {BARS.map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-t-sm transition-all duration-300 hover:opacity-80"
            style={{
              height: `${h}%`,
              backgroundColor: `rgba(0, 74, 198, ${0.1 + (h / 100) * 0.9})`,
            }}
          ></div>
        ))}
      </div>
    </DashboardCard>
  );
};
