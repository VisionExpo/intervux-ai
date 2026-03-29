import { useEffect, useState } from "react";
import { authFetch } from "../hooks/useAuth";

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
}

interface SelectedDetail {
  interview: InterviewRecord;
}

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  const pct = value ?? 0;
  return (
    <div className="score-bar-item">
      <span className="score-label">{label}</span>
      <div className="score-bar">
        <div className="score-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="score-number">{value !== null ? value.toFixed(0) : "-"}</span>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`status-badge status-${status}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function InterviewHistory() {
  const [interviews, setInterviews] = useState<InterviewRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<SelectedDetail | null>(null);

  useEffect(() => {
    authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history")
      .then(setInterviews)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading interview history...</div>
      </div>
    );
  }

  const completed = interviews.filter((i) => i.status === "completed" && i.score !== null);
  const avgScore =
    completed.length > 0
      ? completed.reduce((sum, i) => sum + (i.score ?? 0), 0) / completed.length
      : null;

  return (
    <div className="page-container">
      <div className="history-header">
        <h1>Interview History</h1>
        <div className="nav-links">
          <a href="#/dashboard">Dashboard</a>
          <a href="#/profile">Profile</a>
          <a href="#/mock-interview">New Interview</a>
          <a href="#/notifications">Notifications</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Summary cards */}
      <div className="dashboard-cards" style={{ marginBottom: "1.5rem" }}>
        <div className="score-card">
          <h3>Total sessions</h3>
          <div className="score-value">{interviews.length}</div>
        </div>
        <div className="score-card">
          <h3>Completed</h3>
          <div className="score-value">{completed.length}</div>
        </div>
        <div className="score-card highlight">
          <h3>Average score</h3>
          <div className="score-value">
            {avgScore !== null ? avgScore.toFixed(0) : "-"}
          </div>
        </div>
      </div>

      <div className="history-content">
        <h2>All sessions</h2>

        {interviews.length === 0 ? (
          <div className="no-interviews">
            <p>No mock interviews yet.</p>
            <a href="#/mock-interview" className="action-button primary" style={{ display: "inline-block", marginTop: "1rem" }}>
              Start your first interview
            </a>
          </div>
        ) : (
          <div className="interview-table">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Overall</th>
                  <th>Technical</th>
                  <th>Communication</th>
                  <th>Reasoning</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
<<<<<<< HEAD
                {interviews.map((interview) => (
                  <tr
                    key={interview.id}
                    className={selected?.interview.id === interview.id ? "selected" : ""}
                    onClick={() =>
                      setSelected(
                        selected?.interview.id === interview.id
                          ? null
                          : { interview }
                      )
                    }
                  >
                    <td>#{interview.interview_number}</td>
                    <td>{new Date(interview.created_at).toLocaleDateString()}</td>
                    <td><StatusBadge status={interview.status} /></td>
                    <td>{interview.score !== null ? interview.score.toFixed(0) : "-"}</td>
                    <td>{interview.technical_score !== null ? interview.technical_score.toFixed(0) : "-"}</td>
                    <td>{interview.communication_score !== null ? interview.communication_score.toFixed(0) : "-"}</td>
                    <td>{interview.reasoning_score !== null ? interview.reasoning_score.toFixed(0) : "-"}</td>
                    <td style={{ color: "var(--color-text-secondary)", fontSize: "0.85rem" }}>
                      {interview.status === "completed" ? "View >" : ""}
                    </td>
                  </tr>
                ))}
=======
                {interviews.map((interview) => {
                  const { label, className } = statusMeta(interview.status);
                  return (
                    <tr
                      key={interview.id}
                      onClick={() => setSelectedInterview(interview)}
                      className={selectedInterview?.id === interview.id ? "selected" : ""}
                    >
                      <td>Interview #{interview.interview_number}</td>
                      <td>{new Date(interview.created_at).toLocaleDateString()}</td>
                      <td><span className={`status-badge ${className}`}>{label}</span></td>
                      <td>{interview.score              !== null ? interview.score.toFixed(0)              : "-"}</td>
                      <td>{interview.technical_score    !== null ? interview.technical_score.toFixed(0)    : "-"}</td>
                      <td>{interview.communication_score !== null ? interview.communication_score.toFixed(0) : "-"}</td>
                      <td>{interview.reasoning_score    !== null ? interview.reasoning_score.toFixed(0)    : "-"}</td>
                    </tr>
                  );
                })}
>>>>>>> 95c2f149078e6e1493dde90169c0aae0273e022c
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail drawer */}
      {selected && (
        <div className="interview-details-modal" onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Mock Interview #{selected.interview.interview_number}</h3>

            <div className="detail-grid">
              <div className="detail-item">
                <label>Date</label>
                <span>{new Date(selected.interview.created_at).toLocaleString()}</span>
              </div>
<<<<<<< HEAD
              {selected.interview.completed_at && (
                <div className="detail-item">
                  <label>Completed</label>
                  <span>{new Date(selected.interview.completed_at).toLocaleString()}</span>
=======

              {/* Explain abandoned rows clearly */}
              {selectedInterview.status === "abandoned" && (
                <p style={{
                  background: "#f3ede1", border: "1px solid #d9c9b0",
                  borderRadius: 8, padding: "0.75rem", color: "#6c5a3d",
                  fontSize: "0.9rem", margin: "1rem 0",
                }}>
                  This interview was interrupted before completion - no scores were
                  recorded. You can start a new interview from the Mock Interview page.
                </p>
              )}

              {/* Score bars - completed only */}
              {selectedInterview.status === "completed" && selectedInterview.score !== null && (
                <div className="score-breakdown">
                  <h4>Score Breakdown</h4>
                  <div className="score-bars">
                    {([
                      ["Overall",       selectedInterview.score],
                      ["Technical",     selectedInterview.technical_score ?? 0],
                      ["Communication", selectedInterview.communication_score ?? 0],
                      ["Reasoning",     selectedInterview.reasoning_score ?? 0],
                    ] as [string, number][]).map(([label, value]) => (
                      <div key={label} className="score-bar-item">
                        <span className="score-label">{label}</span>
                        <div className="score-bar">
                          <div className="score-fill" style={{ width: `${value}%` }} />
                        </div>
                        <span className="score-number">{value.toFixed(0)}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{ textAlign: "center", marginTop: "1rem" }}>
                    <a href="#/report" className="action-button primary">View Full Report</a>
                  </div>
>>>>>>> 95c2f149078e6e1493dde90169c0aae0273e022c
                </div>
              )}
              <div className="detail-item">
                <label>Status</label>
                <span><StatusBadge status={selected.interview.status} /></span>
              </div>
            </div>

            {selected.interview.score !== null && (
              <div className="score-breakdown">
                <h4>Score breakdown</h4>
                <div className="score-bars">
                  <ScoreBar label="Overall" value={selected.interview.score} />
                  <ScoreBar label="Technical" value={selected.interview.technical_score} />
                  <ScoreBar label="Communication" value={selected.interview.communication_score} />
                  <ScoreBar label="Reasoning" value={selected.interview.reasoning_score} />
                </div>
              </div>
            )}

            <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
              {selected.interview.status === "completed" && (
                <a
                  href="#/report"
                  className="action-button primary"
                  style={{ display: "inline-block", textDecoration: "none" }}
                >
                  View full report
                </a>
              )}
              <button className="close-button" style={{ flex: 1 }} onClick={() => setSelected(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
