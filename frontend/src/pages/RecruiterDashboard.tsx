import { useEffect, useMemo, useState } from "react";

import AIEvaluationDashboard from "../components/dashboard/AIEvaluationDashboard";
import CandidateComparison from "../components/dashboard/CandidateComparison";
import CandidateList from "../components/dashboard/CandidateList";
import InterviewReplay from "../components/dashboard/InterviewReplay";
import InterviewReport from "../components/dashboard/InterviewReport";
import SkillAnalytics from "../components/dashboard/SkillAnalytics";
import { authFetch, useAuth } from "../hooks/useAuth";
import type {
  CandidateComparisonRow,
  CandidateInterviewReport,
  CandidateListItem,
  DashboardTab,
  EvaluationDashboardResponse,
  SkillAnalyticsResponse,
} from "../types";

export default function RecruiterDashboard() {
  const { logout, user } = useAuth();
  const [tab, setTab] = useState<DashboardTab>("candidates");
  const [candidates, setCandidates] = useState<CandidateListItem[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [report, setReport] = useState<CandidateInterviewReport | null>(null);
  const [analytics, setAnalytics] = useState<SkillAnalyticsResponse | null>(null);
  const [comparisonRows, setComparisonRows] = useState<CandidateComparisonRow[]>([]);
  const [evaluationData, setEvaluationData] = useState<EvaluationDashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const [candidateRows, compareRows] = await Promise.all([
          authFetch<CandidateListItem[]>("/api/candidates"),
          authFetch<CandidateComparisonRow[]>("/api/candidates/compare"),
        ]);
        setCandidates(candidateRows);
        setComparisonRows(compareRows);
        const dashboardMetrics = await authFetch<EvaluationDashboardResponse>("/api/evaluation-dashboard");
        setEvaluationData(dashboardMetrics);
        if (candidateRows.length > 0) {
          setSelectedCandidateId(candidateRows[0].id);
        }
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Failed to load dashboard");
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const selectedCandidate = useMemo(
    () => candidates.find((candidate) => candidate.id === selectedCandidateId) ?? null,
    [candidates, selectedCandidateId]
  );

  useEffect(() => {
    if (!selectedCandidate?.interview_id) {
      setReport(null);
      setAnalytics(null);
      return;
    }
    void (async () => {
      try {
        const [interviewReport, skillAnalytics] = await Promise.all([
          authFetch<CandidateInterviewReport>(`/api/interview/${selectedCandidate.interview_id}`),
          authFetch<SkillAnalyticsResponse>(`/api/interview/${selectedCandidate.interview_id}/analytics`),
        ]);
        setReport(interviewReport);
        setAnalytics(skillAnalytics);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Failed to load candidate report");
      }
    })();
  }, [selectedCandidate?.interview_id]);

  const tabs: Array<{ id: DashboardTab; label: string }> = [
    { id: "candidates", label: "Candidates" },
    { id: "interviews", label: "Interviews" },
    { id: "analytics", label: "Analytics" },
    { id: "evaluation", label: "AI Evaluation" },
  ];

  if (isLoading) {
    return <main className="dashboard-shell">Loading recruiter dashboard...</main>;
  }

  return (
    <main className="dashboard-shell">
      <header>
        <h1>Recruiter Dashboard</h1>
        <div className="header-actions">
          {user && (
            <span className="user-info">
              {user.name} ({user.role})
            </span>
          )}
          <button type="button" className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </header>

      <nav className="top-tabs">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            className={tab === item.id ? "active" : ""}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="dashboard-grid">
        {(tab === "candidates" || tab === "interviews") && (
          <CandidateList
            candidates={candidates}
            selectedCandidateId={selectedCandidateId}
            onSelectCandidate={(candidate) => setSelectedCandidateId(candidate.id)}
          />
        )}

        {tab === "candidates" && <CandidateComparison rows={comparisonRows} />}

        {tab === "interviews" && (
          <>
            <InterviewReport report={report} />
            <InterviewReplay segments={report?.replay_segments ?? []} />
          </>
        )}

        {tab === "analytics" && <SkillAnalytics analytics={analytics} />}

        {tab === "evaluation" && <AIEvaluationDashboard data={evaluationData} />}
      </div>
    </main>
  );
}
