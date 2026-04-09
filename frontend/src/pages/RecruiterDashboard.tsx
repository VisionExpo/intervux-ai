import { useAuth } from "../hooks/useAuth";
import { useRecruiterCandidates, useRecruiterJobPosts } from "../hooks/useDashboardApi";
import { WelcomeHeader } from "../components/dashboard/recruiter/WelcomeHeader";
import { KPIWidgets } from "../components/dashboard/recruiter/KPIWidgets";
import { PipelineOverview } from "../components/dashboard/recruiter/PipelineOverview";
import { ScheduleWidget } from "../components/dashboard/recruiter/ScheduleWidget";
import { CandidateRecommendations } from "../components/dashboard/recruiter/CandidateRecommendations";
import { RecentCandidatesTable } from "../components/dashboard/recruiter/RecentCandidatesTable";
import { ActiveJobsWidget } from "../components/dashboard/recruiter/ActiveJobsWidget";
import { KPISkeleton, CardSkeleton, TableSkeleton } from "../components/shared/SkeletonLoader";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const { data: candidates, isLoading: candLoading, error: candError } = useRecruiterCandidates();
  const { data: jobPosts, isLoading: jobsLoading, error: jobsError } = useRecruiterJobPosts();

  const isLoading = candLoading || jobsLoading;
  const error = candError || jobsError;

  if (isLoading) {
    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="h-20 w-1/3 bg-slate-200 animate-pulse rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <KPISkeleton />
          <KPISkeleton />
          <KPISkeleton />
          <KPISkeleton />
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2 h-[300px] bg-slate-100 animate-pulse rounded-2xl" />
          <CardSkeleton />
        </div>
        <TableSkeleton rows={3} />
      </div>
    );
  }

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <WelcomeHeader userName={user?.name?.split(' ')[0] || "User"} />
      
      {error && (
        <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-3 text-sm text-amber-700 font-medium shadow-sm">
          <span className="material-symbols-outlined text-amber-500">warning</span>
          <span>Connectivity issue: {error}. Showing cached/offline data.</span>
        </div>
      )}

      <KPIWidgets candidates={candidates} jobPosts={jobPosts} />
      
      {/* Pipeline & Upcoming Interviews Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
        <PipelineOverview candidates={candidates} />
        <ScheduleWidget candidates={candidates} />
      </div>

      <CandidateRecommendations />

      {/* Recent Activity Table & Job Snapshot */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 pb-12">
        <RecentCandidatesTable candidates={candidates} />
        <ActiveJobsWidget jobPosts={jobPosts} />
      </div>
    </div>
  );
}
