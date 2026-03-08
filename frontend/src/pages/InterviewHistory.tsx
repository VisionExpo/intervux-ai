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

export default function InterviewHistory() {
  const [interviews, setInterviews] = useState<InterviewRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedInterview, setSelectedInterview] = useState<InterviewRecord | null>(null);

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    try {
      const data = await authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history");
      setInterviews(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load interviews");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading interview history...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="history-header">
        <h1>Interview History</h1>
        <div className="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="#/mock-interview">Mock Interview</a>
          <a href="/notifications">Notifications</a>
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
                  <th>Interview #</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Overall Score</th>
                  <th>Technical</th>
                  <th>Communication</th>
                  <th>Reasoning</th>
                </tr>
              </thead>
              <tbody>
                {interviews.map((interview) => (
                  <tr 
                    key={interview.id} 
                    onClick={() => setSelectedInterview(interview)}
                    className={selectedInterview?.id === interview.id ? "selected" : ""}
                  >
                    <td>Interview #{interview.interview_number}</td>
                    <td>{new Date(interview.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`status-badge status-${interview.status}`}>
                        {interview.status}
                      </span>
                    </td>
                    <td>
                      {interview.score !== null ? (
                        <span className="score">{interview.score.toFixed(0)}</span>
                      ) : (
                        <span className="no-score">-</span>
                      )}
                    </td>
                    <td>
                      {interview.technical_score !== null ? (
                        <span className="score">{interview.technical_score.toFixed(0)}</span>
                      ) : (
                        <span className="no-score">-</span>
                      )}
                    </td>
                    <td>
                      {interview.communication_score !== null ? (
                        <span className="score">{interview.communication_score.toFixed(0)}</span>
                      ) : (
                        <span className="no-score">-</span>
                      )}
                    </td>
                    <td>
                      {interview.reasoning_score !== null ? (
                        <span className="score">{interview.reasoning_score.toFixed(0)}</span>
                      ) : (
                        <span className="no-score">-</span>
                      )}
                    </td>
                  </tr>
                ))}
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
                  <span className={`status-badge status-${selectedInterview.status}`}>
                    {selectedInterview.status}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Session ID:</label>
                  <span>{selectedInterview.session_id}</span>
                </div>
                {selectedInterview.completed_at && (
                  <div className="detail-item">
                    <label>Completed:</label>
                    <span>{new Date(selectedInterview.completed_at).toLocaleString()}</span>
                  </div>
                )}
              </div>

              {selectedInterview.score !== null && (
                <div className="score-breakdown">
                  <h4>Score Breakdown</h4>
                  <div className="score-bars">
                    <div className="score-bar-item">
                      <span className="score-label">Overall</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: `${selectedInterview.score}%` }}></div>
                      </div>
                      <span className="score-number">{selectedInterview.score.toFixed(0)}</span>
                    </div>
                    <div className="score-bar-item">
                      <span className="score-label">Technical</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: `${selectedInterview.technical_score || 0}%` }}></div>
                      </div>
                      <span className="score-number">{selectedInterview.technical_score?.toFixed(0) || "N/A"}</span>
                    </div>
                    <div className="score-bar-item">
                      <span className="score-label">Communication</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: `${selectedInterview.communication_score || 0}%` }}></div>
                      </div>
                      <span className="score-number">{selectedInterview.communication_score?.toFixed(0) || "N/A"}</span>
                    </div>
                    <div className="score-bar-item">
                      <span className="score-label">Reasoning</span>
                      <div className="score-bar">
                        <div className="score-fill" style={{ width: `${selectedInterview.reasoning_score || 0}%` }}></div>
                      </div>
                      <span className="score-number">{selectedInterview.reasoning_score?.toFixed(0) || "N/A"}</span>
                    </div>
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

