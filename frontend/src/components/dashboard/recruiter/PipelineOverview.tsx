import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';
import type { RecruiterCandidate } from '../../../hooks/useDashboardApi';

interface PipelineOverviewProps {
  candidates?: RecruiterCandidate[] | null;
}

export const PipelineOverview: React.FC<PipelineOverviewProps> = ({ candidates }) => {
  // Derive counts from status if the API provided them, else use fallback counts
  // For demo/mock simplicity, we'll partition the real list if available
  const total = candidates?.length ?? 0;
  
  // Simulated partition for visualization
  const screeningCount = Math.floor(total * 0.45);
  const interviewCount = Math.floor(total * 0.2);
  const evalCount = Math.floor(total * 0.1);
  const shortlistedCount = Math.floor(total * 0.05);

  return (
    <DashboardCard className="xl:col-span-2">
      <div className="flex justify-between items-center mb-8">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Pipeline Overview</h3>
        <button className="text-xs font-semibold text-primary hover:underline">View All Roles</button>
      </div>
      <div className="grid grid-cols-6 gap-2">
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-100 dark:bg-slate-200 rounded-xl relative overflow-hidden group">
            <div className="absolute bottom-0 left-0 w-full bg-primary/20 h-full transition-all group-hover:bg-primary/30"></div>
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-slate-800">{total}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 text-center">Applied</span>
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-100 dark:bg-slate-200 rounded-xl relative overflow-hidden group">
            <div className="absolute bottom-0 left-0 w-full bg-primary/40 h-[70%] transition-all"></div>
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-slate-800">{screeningCount}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 text-center">Screening</span>
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-100 dark:bg-slate-200 rounded-xl relative overflow-hidden group">
            <div className="absolute bottom-0 left-0 w-full bg-primary/60 h-[40%] transition-all"></div>
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-slate-800">{interviewCount}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 text-center">Interview</span>
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-100 dark:bg-slate-200 rounded-xl relative overflow-hidden group">
            <div className="absolute bottom-0 left-0 w-full bg-primary/80 h-[25%] transition-all"></div>
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-slate-800">{evalCount}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 text-center">Evaluation</span>
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-100 dark:bg-slate-200 rounded-xl relative overflow-hidden group">
            <div className="absolute bottom-0 left-0 w-full bg-primary h-[15%] transition-all"></div>
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-slate-800">{shortlistedCount}</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 text-center">Shortlisted</span>
        </div>
        <div className="flex flex-col gap-3">
          <div className="h-32 bg-slate-50 dark:bg-slate-100 rounded-xl relative overflow-hidden group border-2 border-dashed border-slate-200">
            <div className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-emerald-600">0</div>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-bold text-emerald-600 text-center">Hired</span>
        </div>
      </div>
    </DashboardCard>
  );
};
