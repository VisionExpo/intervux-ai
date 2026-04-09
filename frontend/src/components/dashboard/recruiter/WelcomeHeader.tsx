import React from 'react';

interface WelcomeHeaderProps {
  userName: string;
}

export const WelcomeHeader: React.FC<WelcomeHeaderProps> = ({ userName }) => {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
      <div className="space-y-1">
        <h2 className="text-2xl font-bold font-headline tracking-tight text-slate-900 dark:text-white">Dashboard Home</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">Welcome back, {userName}. Here’s what’s happening in your hiring pipeline today.</p>
      </div>
      <div className="flex gap-3">
        <button className="px-5 py-2.5 bg-surface-container-lowest dark:bg-slate-800 text-slate-900 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl font-semibold text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-all flex items-center gap-2 shadow-sm">
          <span className="material-symbols-outlined text-sm">person_add</span>
          Invite Candidate
        </button>
        <button className="px-5 py-2.5 bg-primary text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/10">
          <span className="material-symbols-outlined text-sm">post_add</span>
          New Job Post
        </button>
      </div>
    </div>
  );
};
