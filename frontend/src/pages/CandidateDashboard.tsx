import { useAuth } from '../hooks/useAuth';
import { useCandidateDashboard, useCandidateProfile } from '../hooks/useDashboardApi';
import { HeroGreeting } from '../components/dashboard/candidate/HeroGreeting';
import { UpcomingInterview } from '../components/dashboard/candidate/UpcomingInterview';
import { NextStepsChecklist } from '../components/dashboard/candidate/NextStepsChecklist';
import { PerformanceSummary } from '../components/dashboard/candidate/PerformanceSummary';
import { AIInsightsCard } from '../components/dashboard/candidate/AIInsightsCard';

export default function CandidateDashboard() {
  const { user } = useAuth();
  const { data: dashboard, isLoading: dashLoading } = useCandidateDashboard();
  const { data: profile, isLoading: profileLoading } = useCandidateProfile();

  const firstName = profile?.name?.split(' ')[0] || user?.name?.split(' ')[0] || 'Candidate';
  const isLoading = dashLoading || profileLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-slate-500 font-medium">Loading your workspace…</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <HeroGreeting
        userName={firstName}
        applicationStatus={dashboard?.mock_interviews_remaining !== undefined && dashboard.mock_interviews_remaining > 0 ? 'Active' : 'Complete'}
        matchScore={dashboard?.profile_score ? `${dashboard.profile_score.toFixed(0)}% Profile` : '—'}
      />

      {/* Bento grid — main focal row */}
      <div className="grid grid-cols-12 gap-6 mb-6">
        <UpcomingInterview />
        <NextStepsChecklist
          resumeUploaded={!!profile?.resume_url}
          profileScore={dashboard?.profile_score ?? 0}
          mockInterviewScore={dashboard?.mock_interview_score ?? 0}
        />
      </div>

      {/* Performance & AI Insights row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12">
        <PerformanceSummary
          profileScore={dashboard?.profile_score ?? 0}
          resumeScore={dashboard?.resume_score ?? 0}
          interviewScore={dashboard?.mock_interview_score ?? 0}
        />
        <AIInsightsCard
          recentActivity={dashboard?.recent_activity ?? []}
          skills={profile?.skills ?? []}
        />
      </div>
    </>
  );
}
