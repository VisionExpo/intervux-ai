import { useEffect, useRef } from "react";
import { useInterview } from "../hooks/useInterview";
import { audioFeedback } from "../utils/audioFeedback";
import {
  InterviewLayout,
  AvatarInterviewer,
  CodingSandbox,
  CandidateCamera,
  TranscriptPanel,
} from "../components/interview";

export default function InterviewPage() {
  const {
    stage,
    avatarState,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    lastEvaluation,
    finalReport,
    audioRef,
    visemes,
    emotion,
    transcriptMessages,
    mediaStream,
    startAudioStream,
    stopAudioStream,
    lastError,
    uploadResume,
  } = useInterview();

  const prevStageRef = useRef(stage);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await uploadResume(file);
    }
  };

  const connectionStatus = isConnected
    ? "connected"
    : stage === "CONNECTING"
    ? "connecting"
    : "disconnected";

  const isListening = stage === "LISTENING";
  const currentQuestion = lastEvaluation?.question || avatarText;

  useEffect(() => {
    if (stage === "LISTENING") {
      startAudioStream();
    } else {
      stopAudioStream();
    }
  }, [stage, startAudioStream, stopAudioStream]);

  useEffect(() => {
    if (prevStageRef.current !== stage) {
      console.log(`Stage transition: ${prevStageRef.current} -> ${stage}`);
      switch (stage) {
        case "LISTENING":
          audioFeedback.listeningStart();
          break;
        case "PROCESSING_ANSWER":
          audioFeedback.processing();
          break;
        case "ASKING_QUESTION":
        case "NEXT_QUESTION":
          audioFeedback.questionEnd();
          break;
        case "INTERVIEW_COMPLETE":
          audioFeedback.interviewComplete();
          break;
      }
      prevStageRef.current = stage;
    }
  }, [stage]);

  useEffect(() => {
    return () => {
      audioFeedback.dispose();
    };
  }, []);

  useEffect(() => {
    if (stage === "INTERVIEW_COMPLETE" && finalReport) {
      sessionStorage.setItem("interview_report", JSON.stringify(finalReport));
      window.location.hash = "#/report";
    }
  }, [stage, finalReport]);

  if (stage === "INTERVIEW_COMPLETE" && finalReport) {
    return null;
  }

  if (stage === "CONNECTING") {
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

  const showResumeUpload = stage === "WAITING_RESUME" || stage === "PROCESSING_RESUME";

  const getResumeUploadText = () => {
    if (stage === "PROCESSING_RESUME") {
      return "Analyzing your experience...";
    }
    return "Please upload your resume to start the interview. The AI will use it to personalize questions.";
  };
  
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
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>
              {stage === "PROCESSING_RESUME" ? "⏳" : "📄"}
            </div>
            <h2 style={{ color: "#1a2940", marginBottom: "1rem" }}>
              {stage === "PROCESSING_RESUME" ? "Processing Resume" : "Upload Your Resume"}
            </h2>
            <p style={{ color: "#556174", marginBottom: "1.5rem" }}>
              {getResumeUploadText()}
            </p>
            {stage === "WAITING_RESUME" && (
              <div style={{ marginBottom: "1rem" }}>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileSelect}
                  style={{
                    padding: "0.5rem",
                    border: "1px solid #d2dde9",
                    borderRadius: "8px",
                    background: "#fff"
                  }}
                />
              </div>
            )}
          </div>
        ) : (
          <AvatarInterviewer
            isSpeaking={isSpeaking}
            audioRef={audioRef}
            visemes={visemes}
            avatarState={avatarState}
            emotion={emotion}
            questionText={currentQuestion}
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
      cameraPanel={<CandidateCamera isEnabled={true} stream={mediaStream} />}
    />
  );
}
