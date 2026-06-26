import { useEffect, useRef } from "react";

export interface TranscriptMessage {
  id: string;
  speaker: "ai" | "candidate";
  text: string;
  timestamp?: Date;
}

interface TranscriptPanelProps {
  messages: TranscriptMessage[];
  isListening?: boolean;
  onEndAnswer?: () => void;
}

export default function TranscriptPanel({ messages, isListening = false, onEndAnswer }: TranscriptPanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <>
      <div className="transcript-header">
        Transcript
        {isListening && (
          <span style={{ marginLeft: "0.5rem", fontSize: "0.75rem", color: "#22c55e", fontWeight: 400 }}>
            ● Recording
          </span>
        )}
      </div>
      <div className="transcript-messages">
        {messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "#94a3b8", padding: "2rem 0" }}>
            <p>No conversation yet.</p>
            <p style={{ fontSize: "0.75rem" }}>
              {isListening ? "Speak now..." : "Waiting for interview to start..."}
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`transcript-message ${msg.speaker} slide-in`}>
              <div className="transcript-speaker">
                {msg.speaker === "ai" ? "AI Interviewer" : "You"}
              </div>
              <div className="transcript-text">{msg.text}</div>
            </div>
          ))
        )}
        
        {/* Listening indicator */}
        {isListening && (
          <div className="transcript-message candidate slide-in">
            <div className="transcript-speaker">You</div>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
            {onEndAnswer && (
              <div style={{ marginTop: "10px", textAlign: "right" }}>
                <button 
                  onClick={onEndAnswer}
                  style={{
                    padding: "6px 12px",
                    backgroundColor: "#3b82f6",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "0.875rem",
                    fontWeight: 500,
                  }}
                >
                  Done Speaking
                </button>
              </div>
            )}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </>
  );
}

