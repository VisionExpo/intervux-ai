import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

interface Recruiter {
  initials: string;
  bgColor: string;
  textColor: string;
  name: string;
  openRoles: number;
  candidates: number;
  score: string;
  trend: 'up' | 'flat';
}

const RECRUITERS: Recruiter[] = [
  { initials: 'AS', bgColor: 'bg-primary-fixed', textColor: 'text-on-primary-fixed', name: 'Adrian Sterling', openRoles: 12, candidates: 142, score: '8.4/10', trend: 'up' },
  { initials: 'EL', bgColor: 'bg-secondary-fixed', textColor: 'text-on-secondary-fixed', name: 'Elena Lund', openRoles: 8, candidates: 94, score: '7.9/10', trend: 'flat' },
  { initials: 'MK', bgColor: 'bg-tertiary-fixed', textColor: 'text-on-tertiary-fixed', name: 'Marcus Kael', openRoles: 24, candidates: 312, score: '9.1/10', trend: 'up' },
];

export const RecruiterPerformanceTable: React.FC = () => {
  return (
    <DashboardCard noPadding>
      <div className="flex justify-between items-center p-8 pb-6">
        <h4 className="font-headline text-lg font-bold text-slate-900 dark:text-slate-800">Recruiter Performance Overview</h4>
        <button className="text-sm font-semibold text-primary hover:underline">View Full Leaderboard</button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-surface-container-high">
            <tr>
              <th className="px-4 py-3 text-xs font-semibold text-slate-600 rounded-l-lg">Recruiter Name</th>
              <th className="px-4 py-3 text-xs font-semibold text-slate-600">Open Roles</th>
              <th className="px-4 py-3 text-xs font-semibold text-slate-600">Candidates Managed</th>
              <th className="px-4 py-3 text-xs font-semibold text-slate-600 rounded-r-lg">Avg Score Trend</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10">
            {RECRUITERS.map(({ initials, bgColor, textColor, name, openRoles, candidates, score, trend }) => (
              <tr key={name} className="hover:bg-surface transition-colors">
                <td className="px-4 py-5">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full ${bgColor} flex items-center justify-center font-bold text-xs ${textColor}`}>
                      {initials}
                    </div>
                    <span className="font-semibold text-sm text-slate-900 dark:text-slate-800">{name}</span>
                  </div>
                </td>
                <td className="px-4 py-5 text-sm text-slate-700">{openRoles}</td>
                <td className="px-4 py-5 text-sm text-slate-700">{candidates}</td>
                <td className="px-4 py-5">
                  <div className="flex items-center gap-2">
                    <span className={`material-symbols-outlined text-sm ${trend === 'up' ? 'text-primary' : 'text-slate-400'}`}>
                      {trend === 'up' ? 'trending_up' : 'trending_flat'}
                    </span>
                    <span className="text-sm font-bold">{score}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </DashboardCard>
  );
};
