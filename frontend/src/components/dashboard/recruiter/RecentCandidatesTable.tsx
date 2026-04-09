import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';
import type { RecruiterCandidate } from '../../../hooks/useDashboardApi';

interface RecentCandidatesTableProps {
  candidates?: RecruiterCandidate[] | null;
}

function getInitials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

export const RecentCandidatesTable: React.FC<RecentCandidatesTableProps> = ({ candidates }) => {
  const rows = candidates?.slice(0, 10) ?? [];
  const totalCount = candidates?.length ?? 0;

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
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500">Applied</th>
              <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-slate-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-slate-200">
            {rows.length > 0 ? rows.map((c) => (
              <tr key={c.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-100 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-200 flex items-center justify-center text-xs font-bold text-slate-600">
                      {getInitials(c.name)}
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-slate-900 dark:text-slate-800 block">{c.name}</span>
                      <span className="text-[10px] text-slate-400">{c.email}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-xs text-slate-600">{c.role || '—'}</td>
                <td className="px-6 py-4 text-xs text-slate-500">{new Date(c.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4 text-right">
                  <button className="text-xs font-bold text-primary-container hover:underline">Review</button>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-sm text-slate-400">
                  No candidates yet. Invite candidates to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {totalCount > 10 && (
        <div className="p-4 bg-slate-50/50 dark:bg-slate-100 text-center">
          <button className="text-xs font-bold text-slate-500 hover:text-slate-900 transition-colors">
            View All {totalCount} Candidates
          </button>
        </div>
      )}
    </DashboardCard>
  );
};
