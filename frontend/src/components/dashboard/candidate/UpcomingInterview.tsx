import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

interface UpcomingInterviewProps {
  interviewScheduled?: boolean;
}

export const UpcomingInterview: React.FC<UpcomingInterviewProps> = ({ interviewScheduled = false }) => {
  if (!interviewScheduled) {
    return (
      <DashboardCard className="col-span-12 md:col-span-8 relative overflow-hidden group border-2 border-dashed border-slate-200 bg-slate-50/30 flex flex-col items-center justify-center min-h-[220px]">
        <span className="material-symbols-outlined text-slate-300 text-5xl mb-4">event_available</span>
        <h3 className="text-lg font-bold text-slate-400 font-headline">No Interviews Scheduled</h3>
        <p className="text-xs text-slate-400 mt-1">Check back once you've been invited to evaluate</p>
        <button className="mt-6 px-4 py-2 bg-white text-slate-600 border border-slate-200 rounded-lg text-xs font-bold hover:border-primary hover:text-primary transition-all">
          Browse Active Jobs
        </button>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard className="col-span-12 md:col-span-8 relative overflow-hidden group hover:shadow-xl transition-shadow duration-500">
      {/* Decorative animated pulse */}
      <div className="absolute top-0 right-0 p-8">
        <div className="w-24 h-24 bg-primary-container/10 rounded-full flex items-center justify-center animate-pulse">
          <span className="material-symbols-outlined text-primary text-4xl">timer</span>
        </div>
      </div>
      {/* Aesthetic blur blob */}
      <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="relative z-10">
        <h3 className="text-2xl font-bold font-headline mb-6 text-slate-900 dark:text-slate-800">Upcoming Interview</h3>
        <div className="flex flex-wrap items-center gap-10">
          <div className="space-y-1">
            <p className="text-4xl font-bold font-headline text-primary tracking-tighter">18h : 42m</p>
            <p className="text-sm text-slate-400 font-medium uppercase tracking-widest">Countdown to Start</p>
          </div>
          <div className="h-12 w-px bg-slate-100 hidden md:block"></div>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center">
                <span className="material-symbols-outlined text-slate-600">calendar_month</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-800">Tomorrow, at 10:00 AM</p>
                <p className="text-xs text-slate-500">Duration: 90m EST</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface-container-low flex items-center justify-center">
                <span className="material-symbols-outlined text-slate-600">video_call</span>
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-800">Final Candidate Review</p>
                <p className="text-xs text-slate-500">Hosted on Intervux AI Video</p>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="#/mock-interview"
            className="bg-primary text-white px-6 py-2.5 rounded-lg font-semibold flex items-center gap-2 hover:bg-blue-700 transition-colors text-sm"
          >
            <span className="material-symbols-outlined text-sm">play_circle</span>
            Join Preparation Room
          </a>
          <button className="bg-surface-container-low text-slate-700 px-6 py-2.5 rounded-lg font-semibold hover:bg-surface-container-high transition-colors text-sm">
            View Technical Brief
          </button>
        </div>
      </div>
    </DashboardCard>
  );
};
