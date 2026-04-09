import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';
import type { RecruiterCandidate } from '../../../hooks/useDashboardApi';

interface ScheduleWidgetProps {
  candidates?: RecruiterCandidate[] | null;
}

export const ScheduleWidget: React.FC<ScheduleWidgetProps> = ({ candidates }) => {
  const scheduled = candidates?.filter(c => c.interview_id) ?? [];

  return (
    <DashboardCard>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold font-headline text-slate-900 dark:text-slate-800">Today's Schedule</h3>
        <span className="text-[10px] font-bold px-2 py-1 bg-slate-100 text-slate-500 uppercase rounded-full">
          {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        </span>
      </div>
      <div className="space-y-4">
        {scheduled.length > 0 ? scheduled.map((c, i) => (
          <div key={c.id} className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-100 transition-all border border-transparent hover:border-slate-100">
            <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-500 uppercase">
              {c.name[0]}
            </div>
            <div className="flex-1">
              <p className="text-xs font-bold text-slate-900 dark:text-slate-800">{c.name}</p>
              <p className="text-[10px] text-slate-500">{c.role} • {10 + i}:00 AM</p>
            </div>
            <button className={`px-3 py-1.5 text-[10px] font-bold rounded-lg transition-colors ${i === 0 ? 'bg-primary text-white hover:bg-blue-700' : 'bg-surface-container text-slate-600 cursor-not-allowed'}`}>
              {i === 0 ? 'Join' : 'Wait'}
            </button>
          </div>
        )) : (
          <div className="py-8 text-center bg-slate-50 rounded-xl">
             <p className="text-xs text-slate-400 font-medium">No interviews scheduled today</p>
          </div>
        )}
      </div>
      <button className="w-full mt-6 py-2.5 text-[11px] font-bold text-slate-500 bg-slate-50 hover:bg-slate-100 rounded-xl transition-all">
        View Full Calendar
      </button>
    </DashboardCard>
  );
};
