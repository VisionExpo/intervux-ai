import { useAdminEvaluationDashboard } from '../hooks/useDashboardApi';
import { AdminKPIRow } from '../components/dashboard/admin/AdminKPIRow';
import { ActivityTrendsChart } from '../components/dashboard/admin/ActivityTrendsChart';
import { RecruiterPerformanceTable } from '../components/dashboard/admin/RecruiterPerformanceTable';
import { PriorityAlerts } from '../components/dashboard/admin/PriorityAlerts';
import { AIIntelligencePanel } from '../components/dashboard/admin/AIIntelligencePanel';
import { CostAnalyticsPanel } from '../components/dashboard/admin/CostAnalyticsPanel';
import { SystemHealthGrid } from '../components/dashboard/admin/SystemHealthGrid';
import { KPISkeleton, CardSkeleton, TableSkeleton } from '../components/shared/SkeletonLoader';

export default function AdminDashboard() {
  const { data, isLoading, error } = useAdminEvaluationDashboard();

  if (isLoading) {
    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex justify-between items-center mb-8">
          <div className="space-y-2 w-1/4">
            <div className="h-8 bg-slate-200 animate-pulse rounded-lg" />
            <div className="h-4 w-1/2 bg-slate-100 animate-pulse rounded-lg" />
          </div>
          <div className="flex gap-4 w-1/3">
             <div className="h-10 flex-1 bg-slate-100 animate-pulse rounded-lg" />
             <div className="h-10 flex-1 bg-slate-100 animate-pulse rounded-lg" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <KPISkeleton />
          <KPISkeleton />
          <KPISkeleton />
          <KPISkeleton />
        </div>
        <div className="grid grid-cols-12 gap-8">
          <div className="col-span-9 space-y-8">
            <div className="h-[300px] bg-slate-100 animate-pulse rounded-2xl" />
            <TableSkeleton rows={4} />
          </div>
          <div className="col-span-3 space-y-6">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Page header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold font-headline tracking-tight text-slate-900 dark:text-slate-800">Admin Global Metrics</h2>
          <div className="flex items-center gap-4 mt-1 text-sm font-medium text-slate-500">
            <span className="text-blue-600 border-b-2 border-blue-600 pb-0.5 cursor-pointer">Real-time</span>
            <span className="hover:text-blue-500 cursor-pointer transition-colors">Historical</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-2 bg-surface-container rounded-lg text-sm font-medium">
            <span className="material-symbols-outlined text-sm">calendar_today</span>
            Last 30 Days
            <span className="material-symbols-outlined text-sm">expand_more</span>
          </div>
          <button className="hidden sm:block px-4 py-2 text-sm font-semibold bg-surface-container-high rounded-lg hover:bg-slate-200 transition-colors">
            Generate Report
          </button>
          <button className="px-6 py-2 text-sm font-semibold bg-primary text-on-primary rounded-lg active:scale-95 transition-transform shadow-md hover:shadow-lg">
            Export
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-error-container/20 border border-error/20 rounded-xl text-sm text-error font-medium animate-in slide-in-from-top-4 duration-500">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">error</span>
            <span>Failed to load metrics: {error}. Showing cached data.</span>
          </div>
        </div>
      )}

      {/* KPI hero row — wired to API when data is available */}
      <AdminKPIRow evaluationData={data} />

      {/* Main analytics + sidebar */}
      <div className="grid grid-cols-12 gap-8 mb-8">
        <div className="col-span-12 lg:col-span-9 space-y-8">
          <ActivityTrendsChart />
          <RecruiterPerformanceTable />
        </div>
        <div className="col-span-12 lg:col-span-3 space-y-6">
          <PriorityAlerts alerts={data?.alerts} />
          <AIIntelligencePanel evaluationData={data} />
          <CostAnalyticsPanel evaluationData={data} />
        </div>
      </div>

      {/* System health */}
      <SystemHealthGrid evaluationData={data} />
    </div>
  );
}
