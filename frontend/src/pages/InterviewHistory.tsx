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

// Human-readable label + CSS class for every possible status value
const STATUS_META: Record<string, { label: string; className: string }> = {
  completed:   { label: "Completed",   className: "status-completed" },
  in_progress: { label: "In Progress", className: "status-in_progress" },
  abandoned:   { label: "Abandoned",   className: "status-abandoned" },
};

function statusMeta(status: string) {
  return STATUS_META[status] ?? { label: status, className: "" };
}

export default function InterviewHistory() {
  const [interviews, setInterviews] = useState<InterviewRecord[]>([]);
  const [isLoading, setIsLoading]   = useState(true);
  const [error, setError]           = useState("");
  const [selectedInterview, setSelectedInterview] =
    useState<InterviewRecord | null>(null);

  useEffect(() => { fetchInterviews(); }, []);

  const fetchInterviews = async () => {
    try {
      const data = await authFetch<InterviewRecord[]>(
        "/api/candidate/mock-interview/history"
      );
      setInterviews(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load interviews");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="page-container"><div className="loading">Loading interview history...</div></div>;
  }

  return (
    <div className="page-container">
      <div className="history-header">
        <h1>Interview History</h1>
        {/* All links use #/ so browser refresh doesn't 404 */}
        <div className="nav-links">
          <a href="#/dashboard">Dashboard</a>
          <a href="#/profile">Profile</a>
          <a href="#/mock-interview">Mock Interview</a>
          <a href="#/notifications">Notifications</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="history-content">
        <h2>All Mock Interviews</h2>

        {interviews.length === 0 ? (
          <div className="no-interviews">
            <p>You haven't taken any mock interviews yet.</p>
            <a href="#/mock-interview" className="action-button primary">
              Start Your First Interview
            </a>
          </div>
        ) : (
          <div className="interview-table">
            <table>
              <thead>
                <tr>
                  <th>Interview #</th><th>Date</th><th>Status</th>
                  <th>Overall</th><th>Technical</th><th>Communication</th><th>Reasoning</th>
                </tr>
              </thead>
              <tbody>
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
              </tbody>
            </table>
          </div>
        )}

        {selectedInterview && (
          <div className="interview-details-modal" onClick={() => setSelectedInterview(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h3>Interview #{selectedInterview.interview_number} Details</h3>

              <div className="detail-grid">
                <div className="detail-item">
                  <label>Date:</label>
                  <span>{new Date(selectedInterview.created_at).toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <label>Status:</label>
                  <span className={`status-badge ${statusMeta(selectedInterview.status).className}`}>
                    {statusMeta(selectedInterview.status).label}
                  </span>
                </div>
                {selectedInterview.completed_at && (
                  <div className="detail-item">
                    <label>Completed:</label>
                    <span>{new Date(selectedInterview.completed_at).toLocaleString()}</span>
                  </div>
                )}
              </div>

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
                </div>
              )}

              <button onClick={() => setSelectedInterview(null)} className="close-button">
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
