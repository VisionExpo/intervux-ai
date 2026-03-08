import type { ReactNode } from "react";

interface InterviewLayoutProps {
  avatarPanel: ReactNode;
  codingPanel: ReactNode;
  transcriptPanel: ReactNode;
  cameraPanel: ReactNode;
  connectionStatus?: "connected" | "connecting" | "disconnected";
  questionNumber?: number;
  totalQuestions?: number;
}

export default function InterviewLayout({
  avatarPanel,
  codingPanel,
  transcriptPanel,
  cameraPanel,
  connectionStatus = "connecting",
  questionNumber = 0,
  totalQuestions = 0,
}: InterviewLayoutProps) {
  return (
    <div className="interview-layout">
      {/* Connection Status Banner */}
      <div className={`connection-status ${connectionStatus}`}>
        {connectionStatus === "connected" && "🟢 Connected"}
        {connectionStatus === "connecting" && "🟡 Connecting..."}
        {connectionStatus === "disconnected" && "🔴 Disconnected"}
      </div>

      {/* Top Left - AI Interviewer */}
      <div className="avatar-interviewer">
        {avatarPanel}
      </div>

      {/* Top Right - Coding Sandbox */}
      <div className="coding-sandbox">
        {codingPanel}
      </div>

      {/* Bottom - Transcript Panel */}
      <div className="transcript-panel">
        {transcriptPanel}
      </div>

      {/* Bottom Right - Candidate Camera */}
      <div className="candidate-camera">
        {cameraPanel}
      </div>

      {/* Question Progress */}
      {totalQuestions > 0 && (
        <div
          style={{
            position: "fixed",
            bottom: "1rem",
            right: "1rem",
            padding: "0.5rem 1rem",
            background: "rgba(255,255,255,0.9)",
            borderRadius: "20px",
            fontSize: "0.875rem",
            fontWeight: 500,
            boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
          }}
        >
          Question {questionNumber} / {totalQuestions}
        </div>
      )}
    </div>
  );
}

