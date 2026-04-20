import { useEffect, useState } from "react";
import { authFetch } from "../hooks/authFetch";

interface InterviewRecord {
  id: number;
  session_id: string;
  score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  reasoning_score: number | null;
  status: string;
  interview_number: number;
  created_at: string;
  completed_at: string | null;
  evaluation?: string | null;
}

interface PerQuestionEval {
  question: string;
  skill: string;
  scores: Record<string, number> | null;
  summary: string | null;
}

interface PersistedEvaluation {
  final_report?: {
    strengths?: string[];
    weaknesses?: string[];
    overall_recommendation?: string;
    final_summary?: string;
  };
  per_question?: PerQuestionEval[];
}

interface ReportData {
  interview: InterviewRecord;
  strengths: string[];
  weaknesses: string[];
  perQuestion: PerQuestionEval[];
  recommendation: string;
  summary: string;
}

function parseEvaluation(raw: string | null | undefined): PersistedEvaluation | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PersistedEvaluation;
  } catch {
    return null;
  }
}

function deriveStrengthsWeaknesses(
  interview: InterviewRecord,
  evaluation: PersistedEvaluation | null
): { strengths: string[]; weaknesses: string[] } {
  const reportStrengths = evaluation?.final_report?.strengths ?? [];
  const reportWeaknesses = evaluation?.final_report?.weaknesses ?? [];

  if (reportStrengths.length > 0 || reportWeaknesses.length > 0) {
    return { strengths: reportStrengths, weaknesses: reportWeaknesses };
  }

  const perQ = evaluation?.per_question ?? [];
  if (perQ.length > 0) {
    const strengths: string[] = [];
    const weaknesses: string[] = [];
    for (const q of perQ) {
      if (!q.scores) continue;
      const vals = Object.values(q.scores).filter((v): v is number => typeof v === "number");
      if (vals.length === 0) continue;
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      const label = q.skill ? `${q.skill} - ${q.question.slice(0, 60)}...` : q.question.slice(0, 80);
      if (avg >= 7) strengths.push(label);
      else if (avg <= 4) weaknesses.push(label);
    }
    if (strengths.length > 0 || weaknesses.length > 0) {
      return { strengths, weaknesses };
    }
  }

  const strengths: string[] = [];
  const weaknesses: string[] = [];
  const { technical_score: tech, communication_score: comm, reasoning_score: reason } = interview;

  if (tech !== null) {
    if (tech >= 75) strengths.push("Strong technical knowledge");
    else if (tech < 60) weaknesses.push("Technical skills need improvement");
  }
  if (comm !== null) {
    if (comm >= 75) strengths.push("Excellent communication");
    else if (comm < 60) weaknesses.push("Communication can be improved");
  }
  if (reason !== null) {
    if (reason >= 75) strengths.push("Strong problem-solving and reasoning");
    else if (reason < 60) weaknesses.push("Reasoning depth needs work");
  }

  return {
    strengths: strengths.length > 0 ? strengths : ["Good attempt"],
    weaknesses: weaknesses.length > 0 ? weaknesses : ["Keep practising"],
  };
}

export default function CandidateInterviewReport() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [sessionReport, setSessionReport] = useState<Record<string, unknown> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLatestReport = async () => {
      const stored = sessionStorage.getItem("interview_report");
      if (stored) {
        try {
          setSessionReport(JSON.parse(stored) as Record<string, unknown>);
          sessionStorage.removeItem("interview_report");
          setIsLoading(false);
          return;
        } catch {
          sessionStorage.removeItem("interview_report");
        }
      }

      try {
        const interviews = await authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history");
        const completedInterview = interviews.find((i) => i.status === "completed" && i.score !== null);

        if (!completedInterview) {
          window.location.hash = "#/interview-history";
          return;
        }

        const evaluation = parseEvaluation(completedInterview.evaluation);
        const { strengths, weaknesses } = deriveStrengthsWeaknesses(completedInterview, evaluation);

        setReport({
          interview: completedInterview,
          strengths,
          weaknesses,
          perQuestion: evaluation?.per_question ?? [],
          recommendation: evaluation?.final_report?.overall_recommendation ?? "",
          summary: evaluation?.final_report?.final_summary ?? "",
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLatestReport();
  }, []);

  if (isLoading) {
    return <div className="page-container"><div className="loading">Loading report...</div></div>;
  }

  if (sessionReport) {
    const summary = String(sessionReport.final_summary ?? sessionReport.summary ?? "Interview completed.");
    const strengths = Array.isArray(sessionReport.strengths) ? sessionReport.strengths.map((s) => String(s)) : [];
    const weaknesses = Array.isArray(sessionReport.weaknesses) ? sessionReport.weaknesses.map((w) => String(w)) : [];

    return (
      <div className="page-container">
        <div className="report-header">
          <h1>Interview Report</h1>
          <div className="nav-links">
            <a href="#/dashboard">Dashboard</a>
            <a href="#/interview-history">History</a>
          </div>
        </div>
        <div className="report-content">
          <p>{summary}</p>
          {strengths.length > 0 && (
            <div className="feedback-column">
              <h3>Strengths</h3>
              <ul className="feedback-list">{strengths.map((s, i) => <li key={i} className="strength-item">{s}</li>)}</ul>
            </div>
          )}
          {weaknesses.length > 0 && (
            <div className="feedback-column">
              <h3>Areas for Improvement</h3>
              <ul className="feedback-list">{weaknesses.map((w, i) => <li key={i} className="weakness-item">{w}</li>)}</ul>
            </div>
          )}
          <div className="report-actions">
            <a href="#/mock-interview" className="action-button primary">Start New Interview</a>
            <a href="#/dashboard" className="action-button">Back to Dashboard</a>
          </div>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="page-container">
        <div className="report-header">
          <h1>Interview Report</h1>
          <div className="nav-links">
            <a href="#/dashboard">Dashboard</a>
            <a href="#/interview-history">History</a>
          </div>
        </div>
        <div className="report-content">
          <div className="error-message">{error || "No report available"}</div>
          <a href="#/dashboard" className="action-button primary">Back to Dashboard</a>
        </div>
      </div>
    );
  }

  const { interview, strengths, weaknesses, perQuestion, recommendation, summary } = report;
  const scoreDimensions = [
    { label: "Technical", value: interview.technical_score },
    { label: "Communication", value: interview.communication_score },
    { label: "Reasoning", value: interview.reasoning_score },
  ].filter((d): d is { label: string; value: number } => d.value !== null);

  return (
    <div className="page-container">
      <div className="report-header">
        <h1>Interview Completed</h1>
        <div className="nav-links">
          <a href="#/dashboard">Dashboard</a>
          <a href="#/interview-history">History</a>
        </div>
      </div>
      <div className="report-content">
        <div className="report-title">
          <h2>Mock Interview #{interview.interview_number}</h2>
          <p>{interview.completed_at ? new Date(interview.completed_at).toLocaleDateString() : new Date(interview.created_at).toLocaleDateString()}</p>
        </div>

        {interview.score !== null && (
          <div className="overall-score-card">
            <span className="score-label">Overall Score</span>
            <span className="score-value">{interview.score.toFixed(0)}</span>
          </div>
        )}

        {(recommendation || summary) && (
          <div className="bg-[#f4f8fc] border border-[#b8cce3] rounded-xl py-4 px-5 mb-6">
            {recommendation && <p className="m-0 mb-2 font-semibold text-[#1a2940]">Recommendation: <span className="capitalize">{recommendation.replace(/_/g, " ")}</span></p>}
            {summary && <p className="m-0 text-[#3c4b60]">{summary}</p>}
          </div>
        )}

        {scoreDimensions.length > 0 && (
          <div className="score-breakdown">
            <h3>Score Breakdown</h3>
            <div className="score-grid">
              {scoreDimensions.map(({ label, value }) => (
                <div key={label} className="score-item">
                  <span className="score-label">{label}</span>
                  <span className="score-number">{value.toFixed(0)}</span>
                  <div className="score-bar"><div className="score-fill" style={{ width: `${value}%` }} /></div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="feedback-section">
          <div className="feedback-column">
            <h3>Strengths</h3>
            <ul className="feedback-list">{strengths.map((s, i) => <li key={i} className="strength-item">{s}</li>)}</ul>
          </div>
          <div className="feedback-column">
            <h3>Areas for Improvement</h3>
            <ul className="feedback-list">{weaknesses.map((w, i) => <li key={i} className="weakness-item">{w}</li>)}</ul>
          </div>
        </div>

        {perQuestion.length > 0 && (
          <div className="mb-6">
            <h3 className="text-[#1a2940] mb-3">Question Breakdown</h3>
            <div className="grid gap-3">
              {perQuestion.map((q, i) => {
                const vals = q.scores ? Object.values(q.scores).filter((v): v is number => typeof v === "number") : [];
                const avg = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
                return (
                  <div key={i} className="bg-white border border-[#d2dde9] rounded-[10px] py-[0.85rem] px-4">
                    <div className="flex justify-between mb-[0.4rem]">
                      <strong className="text-[#1a2940] text-sm">Q{i + 1}{q.skill ? ` - ${q.skill}` : ""}</strong>
                      {avg !== null && <span className={`font-semibold text-[0.85rem] ${avg >= 7 ? "text-[#2d8a4e]" : avg >= 5 ? "text-[#856404]" : "text-[#c84630]"}`}>{avg.toFixed(1)} / 10</span>}
                    </div>
                    <p className="m-0 mb-[0.35rem] text-[#334155] text-[0.85rem]">{q.question}</p>
                    {q.summary && <p className="m-0 text-[#556174] text-xs italic">{q.summary}</p>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="report-actions">
          <a href="#/mock-interview" className="action-button primary">Start New Interview</a>
          <a href="#/dashboard" className="action-button">Back to Dashboard</a>
        </div>
      </div>
    </div>
  );
}
