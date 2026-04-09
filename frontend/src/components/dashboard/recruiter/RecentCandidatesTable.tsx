import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

export const RecentCandidatesTable: React.FC = () => {
  return (
    <DashboardCard className="xl:col-span-2 overflow-hidden" noPadding>
      <div className="p-6 border-b border-slate-50 dark:border-slate-800 flex justify-between items-center">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Recent Candidates</h3>
        <div className="flex gap-2">
          <button className="p-2 text-slate-400 hover:text-slate-900 transition-colors">
            <span className="material-symbols-outlined text-lg">filter_list</span>
          </button>
          <button className="p-2 text-slate-400 hover:text-slate-900 transition-colors">
            <span className="material-symbols-outlined text-lg">more_horiz</span>
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-surface-container-low/50 dark:bg-slate-100/50">
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Candidate</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Role</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Score</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Status</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-slate-200">
            <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-100 transition-colors">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">JD</div>
                  <span className="text-xs font-semibold text-slate-900 dark:text-slate-800">Jordan Davids</span>
                </div>
              </td>
              <td className="px-6 py-4 text-xs text-slate-600">Growth Marketer</td>
              <td className="px-6 py-4">
                <span className="text-xs font-bold text-primary">8.4</span>
              </td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-full uppercase">Screening</span>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-xs font-bold text-primary-container hover:underline">Review</button>
              </td>
            </tr>
            <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-100 transition-colors">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">KL</div>
                  <span className="text-xs font-semibold text-slate-900 dark:text-slate-800">Kendra Lee</span>
                </div>
              </td>
              <td className="px-6 py-4 text-xs text-slate-600">DevOps Engineer</td>
              <td className="px-6 py-4">
                <span className="text-xs font-bold text-primary">7.9</span>
              </td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 bg-amber-50 text-amber-600 text-[10px] font-bold rounded-full uppercase">Interviewing</span>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-xs font-bold text-primary-container hover:underline">Review</button>
              </td>
            </tr>
            <tr className="hover:bg-slate-50/50 dark:hover:bg-slate-100 transition-colors">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">RM</div>
                  <span className="text-xs font-semibold text-slate-900 dark:text-slate-800">Rahul Mehta</span>
                </div>
              </td>
              <td className="px-6 py-4 text-xs text-slate-600">Data Scientist</td>
              <td className="px-6 py-4">
                <span className="text-xs font-bold text-primary">9.2</span>
              </td>
              <td className="px-6 py-4">
                <span className="px-2 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-full uppercase">Shortlisted</span>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-xs font-bold text-primary-container hover:underline">Review</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="p-4 bg-slate-50/50 dark:bg-slate-100 text-center">
        <button className="text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors">View All 142 Candidates</button>
      </div>
    </DashboardCard>
  );
};
