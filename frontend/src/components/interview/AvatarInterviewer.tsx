import type { RefObject } from "react";
import { useEffect, useState } from "react";
import Avatar3D from "../Avatar3D";
import type { VisemeCue } from "../../avatar/LipSyncController";

type AvatarState = "speaking" | "listening" | "thinking";

interface AvatarInterviewerProps {
  isSpeaking: boolean;
  audioRef: RefObject<HTMLAudioElement | null>;
  visemes?: VisemeCue[];
  avatarState?: AvatarState;
  emotion?: string;
  questionText?: string;
  onStateTransition?: (fromState: AvatarState, toState: AvatarState) => void;
}

export default function AvatarInterviewer({
  isSpeaking,
  audioRef,
  visemes,
  avatarState = "listening",
  emotion = "neutral",
  questionText = "",
  onStateTransition,
}: AvatarInterviewerProps) {
  const [displayState, setDisplayState] = useState<AvatarState>(avatarState);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [pulseEffect, setPulseEffect] = useState(false);

  // Handle state transitions with animation
  useEffect(() => {
    if (displayState !== avatarState) {
      setIsTransitioning(true);
      onStateTransition?.(displayState, avatarState);
      
      // Add pulse effect on state change
      setPulseEffect(true);
      setTimeout(() => setPulseEffect(false), 500);
      
      const timer = setTimeout(() => {
        setDisplayState(avatarState);
        setIsTransitioning(false);
      }, 300);
      
      return () => clearTimeout(timer);
    }
  }, [avatarState, displayState, onStateTransition]);

  // Get display state for indicator
  const getStateDisplay = () => {
    switch (displayState) {
      case "speaking":
        return { icon: "🔊", text: "Speaking", className: "speaking" };
      case "listening":
        return { icon: "🟢", text: "Listening", className: "listening" };
      case "thinking":
        return { icon: "🟡", text: "Thinking...", className: "thinking" };
      default:
        return { icon: "🟡", text: "Thinking...", className: "thinking" };
    }
  };

  const stateDisplay = getStateDisplay();

  return (
    <div 
      style={{ 
        width: "100%", 
        height: "100%", 
        display: "flex", 
        flexDirection: "column",
        transition: "all 0.3s ease",
      }}
      className={`avatar-interviewer-container ${isTransitioning ? "transitioning" : ""}`}
    >
      {/* State Indicator */}
      <div 
        className={`avatar-state-indicator ${stateDisplay.className} ${pulseEffect ? "pulse" : ""}`}
        style={{
          transition: "all 0.3s ease",
          transform: isTransitioning ? "scale(1.05)" : "scale(1)",
        }}
      >
        <span>{stateDisplay.icon}</span>
        <span>{stateDisplay.text}</span>
      </div>

      {/* 3D Avatar */}
      <div 
        style={{ 
          flex: 1, 
          display: "flex", 
          alignItems: "center", 
          justifyContent: "center",
          transition: "all 0.5s ease",
          filter: isTransitioning ? "brightness(1.1)" : "brightness(1)",
        }}
      >
        <Avatar3D
          isSpeacking={isSpeaking}
          audioRef={audioRef}
          visemes={visemes}
          avatarState={displayState}
          emotion={emotion}
        />
      </div>

      {/* Question Display */}
      <div 
        className="question-display"
        style={{
          transition: "all 0.5s ease",
          opacity: questionText ? 1 : 0.7,
        }}
      >
        {questionText ? (
          <p style={{ margin: 0, fontSize: "0.95rem", lineHeight: 1.6, color: "#334155" }}>
            {questionText}
          </p>
        ) : (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
      </div>
    </div>
  );
}

