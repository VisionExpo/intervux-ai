import { useEffect, useMemo, useState } from "react";

import AIEvaluationDashboard from "./AIEvaluationDashboard";
import CandidateComparison from "./CandidateComparison";
import CandidateList from "./CandidateList";
import InterviewReplay from "./InterviewReplay";
import InterviewReport from "./InterviewReport";
import SkillAnalytics from "./SkillAnalytics";
import type {
  CandidateComparisonRow,
  CandidateInterviewReport,
  CandidateListItem,
  DashboardTab,
  EvaluationDashboardResponse,
  SkillAnalyticsResponse,
} from "./types";

const API_BASE_URL = "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status}) for ${path}`);
  }
  return (await response.json()) as T;
}

export default function RecruiterDashboard() {
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
          fetchJson<CandidateListItem[]>("/api/candidates"),
          fetchJson<CandidateComparisonRow[]>("/api/candidates/compare"),
        ]);
        setCandidates(candidateRows);
        setComparisonRows(compareRows);
        const dashboardMetrics = await fetchJson<EvaluationDashboardResponse>("/api/evaluation-dashboard");
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
          fetchJson<CandidateInterviewReport>(`/api/interview/${selectedCandidate.interview_id}`),
          fetchJson<SkillAnalyticsResponse>(`/api/interview/${selectedCandidate.interview_id}/analytics`),
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
