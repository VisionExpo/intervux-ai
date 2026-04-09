import { useAuth } from "../hooks/useAuth";
import { useRecruiterCandidates, useRecruiterJobPosts } from "../hooks/useDashboardApi";
import { WelcomeHeader } from "../components/dashboard/recruiter/WelcomeHeader";
import { KPIWidgets } from "../components/dashboard/recruiter/KPIWidgets";
import { PipelineOverview } from "../components/dashboard/recruiter/PipelineOverview";
import { ScheduleWidget } from "../components/dashboard/recruiter/ScheduleWidget";
import { CandidateRecommendations } from "../components/dashboard/recruiter/CandidateRecommendations";
import { RecentCandidatesTable } from "../components/dashboard/recruiter/RecentCandidatesTable";
import { ActiveJobsWidget } from "../components/dashboard/recruiter/ActiveJobsWidget";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const { data: candidates, isLoading: candLoading } = useRecruiterCandidates();
  const { data: jobPosts, isLoading: jobsLoading } = useRecruiterJobPosts();

  const isLoading = candLoading || jobsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-slate-500 font-medium">Loading dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <WelcomeHeader userName={user?.name?.split(' ')[0] || "User"} />
      <KPIWidgets candidates={candidates} jobPosts={jobPosts} />
      
      {/* Pipeline & Upcoming Interviews Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
        <PipelineOverview />
        <ScheduleWidget />
      </div>

      <CandidateRecommendations />

      {/* Recent Activity Table & Job Snapshot */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 pb-12">
        <RecentCandidatesTable candidates={candidates} />
        <ActiveJobsWidget jobPosts={jobPosts} />
      </div>
    </>
  );
}
