import React from 'react';
import { DashboardCard } from '../shared/DashboardCard';

export const KPIWidgets: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Active Job Posts */}
      <DashboardCard className="!p-6 flex flex-col justify-between h-32" noPadding>
        <div className="flex justify-between items-start">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider font-label">Active Job Posts</span>
          <span className="p-2 bg-blue-50 text-blue-600 rounded-lg material-symbols-outlined text-sm">work</span>
        </div>
        <div className="flex items-end justify-between mt-auto">
          <span className="text-3xl font-bold font-headline dark:text-slate-800">12</span>
          <span className="text-xs font-medium text-green-600 flex items-center">
            <span className="material-symbols-outlined text-sm mr-1">trending_up</span> +2 this week
          </span>
        </div>
      </DashboardCard>

      {/* In Pipeline */}
      <DashboardCard className="!p-6 flex flex-col justify-between h-32" noPadding>
        <div className="flex justify-between items-start">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider font-label">In Pipeline</span>
          <span className="p-2 bg-purple-50 text-purple-600 rounded-lg material-symbols-outlined text-sm">group</span>
        </div>
        <div className="flex items-end justify-between mt-auto">
          <span className="text-3xl font-bold font-headline dark:text-slate-800">248</span>
          <span className="text-xs font-medium text-green-600 flex items-center">
            <span className="material-symbols-outlined text-sm mr-1">trending_up</span> +42 today
          </span>
        </div>
      </DashboardCard>

      {/* Interviews Today */}
      <DashboardCard className="!p-6 flex flex-col justify-between h-32" noPadding>
        <div className="flex justify-between items-start">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider font-label">Interviews Today</span>
          <span className="p-2 bg-orange-50 text-orange-600 rounded-lg material-symbols-outlined text-sm">calendar_today</span>
        </div>
        <div className="flex items-end justify-between mt-auto">
          <span className="text-3xl font-bold font-headline dark:text-slate-800">8</span>
          <span className="text-xs font-medium text-slate-500 flex items-center">
            Next in 45m
          </span>
        </div>
      </DashboardCard>

      {/* Shortlisted */}
      <DashboardCard className="!p-6 flex flex-col justify-between h-32" noPadding>
        <div className="flex justify-between items-start">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider font-label">Shortlisted</span>
          <span className="p-2 bg-emerald-50 text-emerald-600 rounded-lg material-symbols-outlined text-sm">verified</span>
        </div>
        <div className="flex items-end justify-between mt-auto">
          <span className="text-3xl font-bold font-headline dark:text-slate-800">34</span>
          <span className="text-xs font-medium text-green-600 flex items-center">
            <span className="material-symbols-outlined text-sm mr-1">trending_up</span> 14% conversion
          </span>
        </div>
      </DashboardCard>
    </div>
  );
};
