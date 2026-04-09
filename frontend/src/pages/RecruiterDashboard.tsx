import { useAuth } from "../hooks/useAuth";
import { WelcomeHeader } from "../components/dashboard/recruiter/WelcomeHeader";
import { KPIWidgets } from "../components/dashboard/recruiter/KPIWidgets";
import { PipelineOverview } from "../components/dashboard/recruiter/PipelineOverview";
import { ScheduleWidget } from "../components/dashboard/recruiter/ScheduleWidget";
import { CandidateRecommendations } from "../components/dashboard/recruiter/CandidateRecommendations";
import { RecentCandidatesTable } from "../components/dashboard/recruiter/RecentCandidatesTable";
import { ActiveJobsWidget } from "../components/dashboard/recruiter/ActiveJobsWidget";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  
  return (
    <>
      <WelcomeHeader userName={user?.name?.split(' ')[0] || "User"} />
      <KPIWidgets />
      
      {/* Pipeline & Upcoming Interviews Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
        <PipelineOverview />
        <ScheduleWidget />
      </div>

      <CandidateRecommendations />

      {/* Recent Activity Table & Job Snapshot */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 pb-12">
        <RecentCandidatesTable />
        <ActiveJobsWidget />
      </div>
    </>
  );
}
