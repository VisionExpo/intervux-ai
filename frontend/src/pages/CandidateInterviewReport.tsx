import { useEffect, useState } from "react";

// -- Types --------------------------------------------------------------------

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
  evaluation?: string | null; // JSON string persisted by interview_persistence.py
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

// -- Helpers -------------------------------------------------------------------

/**
 * Parse the evaluation JSON string persisted by interview_persistence.py.
 * Returns null if the field is absent, empty, or malformed.
 */
function parseEvaluation(raw: string | null | undefined): PersistedEvaluation | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PersistedEvaluation;
  } catch {
    return null;
  }
}

/**
 * Derive strengths and weaknesses.
 *
 * Priority order:
 *   1. final_report.strengths / .weaknesses from the persisted LLM report
 *   2. Per-question summaries (non-null) as fallback narrative
 *   3. Score-threshold heuristics as a last resort
 */
function deriveStrengthsWeaknesses(
  interview: InterviewRecord,
  evaluation: PersistedEvaluation | null
): { strengths: string[]; weaknesses: string[] } {
  // 1 — use LLM-generated lists if present
  const reportStrengths = evaluation?.final_report?.strengths ?? [];
  const reportWeaknesses = evaluation?.final_report?.weaknesses ?? [];

  if (reportStrengths.length > 0 || reportWeaknesses.length > 0) {
    return { strengths: reportStrengths, weaknesses: reportWeaknesses };
  }

  // 2 — synthesise from per-question summaries
  const perQ = evaluation?.per_question ?? [];
  if (perQ.length > 0) {
    const strengths: string[] = [];
    const weaknesses: string[] = [];
    for (const q of perQ) {
      if (!q.scores) continue;
      const vals = Object.values(q.scores).filter((v): v is number => typeof v === "number");
      if (vals.length === 0) continue;
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      const label = q.skill ? `${q.skill} — ${q.question.slice(0, 60)}…` : q.question.slice(0, 80);
      if (avg >= 7) strengths.push(label);
      else if (avg <= 4) weaknesses.push(label);
    }
    if (strengths.length > 0 || weaknesses.length > 0) {
      return { strengths, weaknesses };
    }
  }

  // 3 — score-threshold heuristics (last resort)
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

// -- Component -----------------------------------------------------------------

export default function CandidateInterviewReport() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLatestReport = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/candidate/mock-interview/history",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
            },
          }
        );

        if (!response.ok) throw new Error("Failed to fetch interview history");

        const interviews: InterviewRecord[] = await response.json();

        // Use the most recent completed interview
        const completedInterview = interviews.find(
          (i) => i.status === "completed" && i.score !== null
        );

        if (!completedInterview) {
          setError("No completed interview report found");
          setIsLoading(false);
          return;
        }

        // Parse the real evaluation payload persisted by interview_persistence.py
        const evaluation = parseEvaluation(completedInterview.evaluation);

        const { strengths, weaknesses } = deriveStrengthsWeaknesses(
          completedInterview,
          evaluation
        );

        // Per-question breakdown (empty array if not present)
        const perQuestion = evaluation?.per_question ?? [];

        // Recommendation and summary from the LLM report if available
        const recommendation =
          evaluation?.final_report?.overall_recommendation ?? "";
        const summary = evaluation?.final_report?.final_summary ?? "";

        setReport({
          interview: completedInterview,
          strengths,
          weaknesses,
          perQuestion,
          recommendation,
          summary,
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
    return (
      <div className="page-container">
        <div className="loading">Loading report...</div>
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
          <a href="#/dashboard" className="action-button primary">
            Back to Dashboard
          </a>
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
          <p>
            {interview.completed_at
              ? new Date(interview.completed_at).toLocaleDateString()
              : new Date(interview.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Overall score */}
        {interview.score !== null && (
          <div className="overall-score-card">
            <span className="score-label">Overall Score</span>
            <span className="score-value">{interview.score.toFixed(0)}</span>
          </div>
        )}

        {/* LLM recommendation + summary */}
        {(recommendation || summary) && (
          <div
            style={{
              background: "#f4f8fc",
              border: "1px solid #b8cce3",
              borderRadius: 12,
              padding: "1rem 1.25rem",
              marginBottom: "1.5rem",
            }}
          >
            {recommendation && (
              <p style={{ margin: "0 0 0.5rem", fontWeight: 600, color: "#1a2940" }}>
                Recommendation:{" "}
                <span style={{ textTransform: "capitalize" }}>{recommendation.replace(/_/g, " ")}</span>
              </p>
            )}
            {summary && (
              <p style={{ margin: 0, color: "#3c4b60" }}>{summary}</p>
            )}
          </div>
        )}

        {/* Score breakdown bars */}
        {scoreDimensions.length > 0 && (
          <div className="score-breakdown">
            <h3>Score Breakdown</h3>
            <div className="score-grid">
              {scoreDimensions.map(({ label, value }) => (
                <div key={label} className="score-item">
                  <span className="score-label">{label}</span>
                  <span className="score-number">{value.toFixed(0)}</span>
                  <div className="score-bar">
                    <div className="score-fill" style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Strengths / weaknesses */}
        <div className="feedback-section">
          <div className="feedback-column">
            <h3>Strengths</h3>
            <ul className="feedback-list">
              {strengths.map((s, i) => (
                <li key={i} className="strength-item">
                  <span className="feedback-icon">?</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>

          <div className="feedback-column">
            <h3>Areas for Improvement</h3>
            <ul className="feedback-list">
              {weaknesses.map((w, i) => (
                <li key={i} className="weakness-item">
                  <span className="feedback-icon">?</span>
                  {w}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Per-question breakdown — only shown when real data is available */}
        {perQuestion.length > 0 && (
          <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ color: "#1a2940", marginBottom: "0.75rem" }}>
              Question Breakdown
            </h3>
            <div style={{ display: "grid", gap: "0.75rem" }}>
              {perQuestion.map((q, i) => {
                const vals = q.scores
                  ? Object.values(q.scores).filter(
                      (v): v is number => typeof v === "number"
                    )
                  : [];
                const avg =
                  vals.length > 0
                    ? vals.reduce((a, b) => a + b, 0) / vals.length
                    : null;

                return (
                  <div
                    key={i}
                    style={{
                      background: "#fff",
                      border: "1px solid #d2dde9",
                      borderRadius: 10,
                      padding: "0.85rem 1rem",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: "0.4rem",
                      }}
                    >
                      <strong style={{ color: "#1a2940", fontSize: "0.9rem" }}>
                        Q{i + 1}
                        {q.skill ? ` · ${q.skill}` : ""}
                      </strong>
                      {avg !== null && (
                        <span
                          style={{
                            color: avg >= 7 ? "#2d8a4e" : avg >= 5 ? "#856404" : "#c84630",
                            fontWeight: 600,
                            fontSize: "0.85rem",
                          }}
                        >
                          {avg.toFixed(1)} / 10
                        </span>
                      )}
                    </div>
                    <p style={{ margin: "0 0 0.35rem", color: "#334155", fontSize: "0.85rem" }}>
                      {q.question}
                    </p>
                    {q.summary && (
                      <p style={{ margin: 0, color: "#556174", fontSize: "0.8rem", fontStyle: "italic" }}>
                        {q.summary}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="report-actions">
          <a href="#/mock-interview" className="action-button primary">
            Start New Interview
          </a>
          <a href="#/dashboard" className="action-button">
            Back to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
