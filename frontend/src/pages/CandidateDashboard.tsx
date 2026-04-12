import { useAuth } from '../hooks/useAuth';
import { useCandidateDashboard, useCandidateProfile } from '../hooks/useDashboardApi';
import { HeroGreeting } from '../components/dashboard/candidate/HeroGreeting';
import { UpcomingInterview } from '../components/dashboard/candidate/UpcomingInterview';
import { NextStepsChecklist } from '../components/dashboard/candidate/NextStepsChecklist';
import { PerformanceSummary } from '../components/dashboard/candidate/PerformanceSummary';
import { AIInsightsCard } from '../components/dashboard/candidate/AIInsightsCard';
import { CardSkeleton } from '../components/shared/SkeletonLoader';

export default function CandidateDashboard() {
  const { user } = useAuth();
  const { data: dashboard, isLoading: dashLoading, error: dashError } = useCandidateDashboard();
  const { data: profile, isLoading: profileLoading, error: profileError } = useCandidateProfile();

  const firstName = profile?.name?.split(' ')[0] || user?.name?.split(' ')[0] || 'Candidate';
  const isLoading = dashLoading || profileLoading;
  const error = dashError || profileError;

  if (isLoading) {
    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="h-48 bg-slate-200 animate-pulse rounded-3xl" />
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-8 bg-slate-100 animate-pulse rounded-2xl h-[300px]" />
          <div className="col-span-4 space-y-4">
             <CardSkeleton />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-6">
           <CardSkeleton />
           <CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
      <HeroGreeting
        userName={firstName}
        applicationStatus={dashboard?.mock_interviews_remaining !== undefined && dashboard.mock_interviews_remaining > 0 ? 'Active' : 'Complete'}
        matchScore={dashboard?.profile_score ? `${dashboard.profile_score.toFixed(0)}% Profile` : '—'}
      />

      {error && (
        <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-3 text-sm text-amber-700 font-medium animate-in slide-in-from-top-4 duration-500 shadow-sm">
          <span className="material-symbols-outlined text-amber-500">warning</span>
          <span>Using offline workspace mode: {error}</span>
        </div>
      )}

      {/* Bento grid — main focal row */}
      <div className="grid grid-cols-12 gap-6 mb-6">
        <UpcomingInterview interviewScheduled={dashboard?.mock_interviews_remaining !== undefined && dashboard.mock_interviews_remaining < 5} />
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
    </div>
  );
}
