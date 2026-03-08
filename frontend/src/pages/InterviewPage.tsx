import { useEffect, useCallback, useRef, useState } from "react";
import { useInterview } from "../hooks/useInterview";
import { audioFeedback } from "../utils/audioFeedback";
import {
  InterviewLayout,
  AvatarInterviewer,
  CodingSandbox,
  CandidateCamera,
  TranscriptPanel,
} from "../components/interview";
import type { AvatarState } from "../hooks/useInterview";

export default function InterviewPage() {
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const {
    stage,
    avatarState,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    isRecording,
    lastEvaluation,
    audioRef,
    visemes,
    emotion,
    transcriptMessages,
    startAudioStream,
    lastError,
    uploadResume,
  } = useInterview();

  const prevStageRef = useRef(stage);
  const prevAvatarStateRef = useRef(avatarState);

  // Handle resume file selection
  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setResumeFile(file);
    }
  };

  // Handle resume upload
  const handleUploadResume = async () => {
    if (!resumeFile) return;
    setIsUploading(true);
    try {
      await uploadResume(resumeFile);
    } catch (err) {
      console.error("Failed to upload resume:", err);
    } finally {
      setIsUploading(false);
    }
  };

  // Show loading while initial connection is being established
  useEffect(() => {
    if (isConnected || lastError) {
      // Give a small delay to show the connection status
      const timer = setTimeout(() => setIsPageLoading(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [isConnected, lastError]);

  // Determine connection status
  const connectionStatus = isConnected
    ? "connected"
    : stage === "connecting"
      ? "connecting"
      : "disconnected";

  // Check if we're in listening state
  const isListening = stage === "listening" || isRecording;

  // Get current question text from avatar or evaluation
  const currentQuestion = lastEvaluation?.question || avatarText;

  // Handle state transitions with audio feedback and natural pauses
  const handleStateTransition = useCallback((fromState: AvatarState, toState: AvatarState) => {
    console.log(`State transition: ${fromState} -> ${toState}`);
    
    // Play appropriate sound based on transition
    if (toState === "listening" && fromState === "speaking") {
      audioFeedback.listeningStart();
      
      // Natural pause before starting to listen
      setTimeout(() => {
        startAudioStream();
      }, 800);
    } else if (toState === "thinking" && fromState === "listening") {
      audioFeedback.processing();
    } else if (toState === "speaking" && fromState === "thinking") {
      audioFeedback.nextQuestion();
    }
  }, [startAudioStream]);

  // Handle stage transitions
  useEffect(() => {
    if (prevStageRef.current !== stage) {
      console.log(`Stage transition: ${prevStageRef.current} -> ${stage}`);
      
      switch (stage) {
        case "listening":
          audioFeedback.listeningStart();
          break;
        case "processing":
          audioFeedback.processing();
          break;
        case "next_question":
        case "asking_question":
          audioFeedback.questionEnd();
          break;
        case "completed":
          audioFeedback.interviewComplete();
          break;
      }
      
      prevStageRef.current = stage;
    }
  }, [stage]);

  // Handle avatar state transitions
  useEffect(() => {
    if (prevAvatarStateRef.current !== avatarState) {
      handleStateTransition(prevAvatarStateRef.current, avatarState);
      prevAvatarStateRef.current = avatarState;
    }
  }, [avatarState, handleStateTransition]);

  // Cleanup audio feedback on unmount
  useEffect(() => {
    return () => {
      audioFeedback.dispose();
    };
  }, []);

  // Show loading screen while connecting
  if (isPageLoading) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        background: "linear-gradient(135deg, #1a2940 0%, #2d4a6f 100%)",
        color: "#fff"
      }}>
        <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>🎙️</div>
        <h2>Connecting to Interview...</h2>
        <p style={{ color: "#94a3b8" }}>Please wait while we establish a connection</p>
        {lastError && (
          <p style={{ color: "#ef4444", marginTop: "1rem" }}>{lastError}</p>
        )}
      </div>
    );
  }

  // Show resume upload UI when waiting for resume
  const showResumeUpload = stage === "waiting_resume" || avatarText.includes("upload your resume");

  return (
    <InterviewLayout
      connectionStatus={connectionStatus}
      questionNumber={questionIndex}
      totalQuestions={totalQuestions}
      avatarPanel={
        showResumeUpload ? (
          <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            padding: "2rem",
            textAlign: "center"
          }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📄</div>
            <h2 style={{ color: "#1a2940", marginBottom: "1rem" }}>Upload Your Resume</h2>
            <p style={{ color: "#556174", marginBottom: "1.5rem" }}>
              Please upload your resume to start the interview. The AI interviewer will use it to personalize questions.
            </p>
            <div style={{ marginBottom: "1rem" }}>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleResumeChange}
                style={{
                  padding: "0.5rem",
                  border: "1px solid #d2dde9",
                  borderRadius: "8px",
                  background: "#fff"
                }}
              />
            </div>
            {resumeFile && (
              <p style={{ color: "#22c55e", marginBottom: "1rem" }}>
                Selected: {resumeFile.name}
              </p>
            )}
            <button
              onClick={handleUploadResume}
              disabled={!resumeFile || isUploading}
              style={{
                padding: "0.75rem 2rem",
                background: resumeFile && !isUploading ? "#c84630" : "#9ca3af",
                color: "#fff",
                border: "none",
                borderRadius: "10px",
                fontSize: "1rem",
                fontWeight: 600,
                cursor: resumeFile && !isUploading ? "pointer" : "not-allowed"
              }}
            >
              {isUploading ? "Uploading..." : "Start Interview"}
            </button>
          </div>
        ) : (
          <AvatarInterviewer
            isSpeaking={isSpeaking}
            audioRef={audioRef}
            visemes={visemes}
            avatarState={avatarState}
            emotion={emotion}
            questionText={currentQuestion}
            onStateTransition={handleStateTransition}
          />
        )
      }
      codingPanel={
        <CodingSandbox
          language="python"
          problemDescription={
            lastEvaluation?.question?.includes("code")
              ? lastEvaluation.question
              : "Implement a function that finds two numbers that add up to a target."
          }
        />
      }
      transcriptPanel={
        <TranscriptPanel
          messages={transcriptMessages}
          isListening={isListening}
        />
      }
      cameraPanel={<CandidateCamera isEnabled={true} />}
    />
  );
}

