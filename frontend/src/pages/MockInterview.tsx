import { useEffect, useState, useRef } from "react";
import { authFetch } from "../hooks/useAuth";

interface InterviewHistory {
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

export default function MockInterview() {
  const [interviewHistory, setInterviewHistory] = useState<InterviewHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState("");
  const [currentInterview, setCurrentInterview] = useState<InterviewHistory | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await authFetch<InterviewHistory[]>("/api/candidate/mock-interview/history");
      setInterviewHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setIsLoading(false);
    }
  };

  const startInterview = async () => {
    setIsStarting(true);
    setError("");

    try {
      // Start the interview session
      const response = await authFetch<{ session_id: string; mock_interview_id: number; message: string }>(
        "/api/candidate/mock-interview/start",
        { method: "POST" }
      );

      // Connect to WebSocket for the interview
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(`${wsProtocol}//localhost:8000/ws/interview`);

      ws.onopen = () => {
        console.log("Connected to interview WebSocket");
        
        // Send resume upload message
        ws.send(JSON.stringify({
          type: "resume_upload",
          file_name: "demo_resume.pdf",
          file_bytes: "" // Empty for demo, would contain base64 in production
        }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received:", data);
        
        if (data.type === "question") {
          // Update UI with question
        } else if (data.type === "evaluation") {
          // Interview completed
          console.log("Interview evaluation:", data);
          fetchHistory(); // Refresh history
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("Connection error during interview");
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
        fetchHistory();
      };

      wsRef.current = ws;

      // For demo purposes, just show that interview started
      alert("Interview session started! In production, you would be connected to the AI interviewer.");
      
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setIsStarting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="interview-header">
        <h1>Mock Interviews</h1>
        <div className="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/profile">Profile</a>
          <a href="/interview-history">History</a>
          <a href="/notifications">Notifications</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="interview-start-section">
        <h2>Start Your Practice Interview</h2>
        <p>Practice with our AI-powered mock interviewer. You'll get 3 free interviews to improve your skills.</p>
        
        <button 
          onClick={startInterview} 
          disabled={isStarting}
          className="start-interview-button"
        >
          {isStarting ? "Starting..." : "Start Mock Interview"}
        </button>
      </div>

      <div className="interview-history-section">
        <h2>Your Interview History</h2>
        
        {interviewHistory.length === 0 ? (
          <p className="no-history">You haven't taken any mock interviews yet.</p>
        ) : (
          <div className="interview-list">
            {interviewHistory.map((interview) => (
              <div key={interview.id} className="interview-card">
                <div className="interview-info">
                  <h3>Mock Interview #{interview.interview_number}</h3>
                  <p className="interview-date">
                    {new Date(interview.created_at).toLocaleDateString()}
                  </p>
                  <p className="interview-status">
                    Status: <span className={`status-${interview.status}`}>{interview.status}</span>
                  </p>
                </div>
                
                {interview.score !== null ? (
                  <div className="interview-scores">
                    <div className="score-item">
                      <span className="score-label">Overall</span>
                      <span className="score-value">{interview.score.toFixed(0)}</span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Technical</span>
                      <span className="score-value">{interview.technical_score?.toFixed(0) || "N/A"}</span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Communication</span>
                      <span className="score-value">{interview.communication_score?.toFixed(0) || "N/A"}</span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Reasoning</span>
                      <span className="score-value">{interview.reasoning_score?.toFixed(0) || "N/A"}</span>
                    </div>
                  </div>
                ) : (
                  <div className="interview-pending">
                    <p>Interview in progress or not completed...</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

