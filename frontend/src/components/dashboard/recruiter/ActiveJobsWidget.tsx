import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';
import type { RecruiterJobPost } from '../../../hooks/useDashboardApi';

interface ActiveJobsWidgetProps {
  jobPosts?: RecruiterJobPost[] | null;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Today';
  if (days === 1) return '1d ago';
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

export const ActiveJobsWidget: React.FC<ActiveJobsWidgetProps> = ({ jobPosts }) => {
  const jobs = jobPosts?.slice(0, 5) ?? [];

  return (
    <DashboardCard>
      <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800 mb-6">Active Jobs</h3>
      <div className="space-y-6">
        {jobs.length > 0 ? jobs.map((job) => (
          <div key={job.id} className="group cursor-pointer">
            <div className="flex justify-between items-start mb-2">
              <h4 className="text-sm font-bold text-slate-900 dark:text-slate-800 group-hover:text-primary transition-colors">
                {job.title}
              </h4>
              <span className="text-[10px] font-bold text-slate-400">{timeAgo(job.created_at)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full uppercase ${
                job.status === 'active' ? 'bg-emerald-50 text-emerald-600' :
                job.status === 'paused' ? 'bg-amber-50 text-amber-600' :
                'bg-slate-100 text-slate-500'
              }`}>
                {job.status}
              </span>
              <span className="text-[10px] font-bold text-slate-600 bg-slate-100 dark:bg-slate-200 px-2 py-1 rounded">
                {job.experience_level}
              </span>
            </div>
          </div>
        )) : (
          <p className="text-sm text-slate-400 text-center py-8">No job posts yet</p>
        )}
      </div>
      
      <button className="w-full mt-8 py-3 border-2 border-dashed border-slate-200 dark:border-slate-300 text-slate-500 rounded-xl text-xs font-bold hover:border-primary hover:text-primary transition-all flex items-center justify-center gap-2">
        <span className="material-symbols-outlined text-sm">add_circle</span>
        Post New Job
      </button>
    </DashboardCard>
  );
};
