import Avatar3D from "../components/Avatar3D";
import { useInterview } from "../hooks/useInterview";

export default function InterviewPage() {
  const {
    stage,
    avatarState,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    partialTranscript,
    isRecording,
    lastEvaluation,
    finalReport,
    lastError,
    audioRef,
    visemes,
    uploadResume,
    sendAudioAnswer,
    startAudioStream,
    stopAudioStream,
  } = useInterview();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "2rem",
        fontFamily: "Arial",
        gap: "1rem",
      }}
    >
      <h1>Intervux AI Voice Interview</h1>
      <p>
        Socket: {isConnected ? "connected" : "disconnected"} | State: {stage}
      </p>
      {lastError && <p style={{ color: "#b00020" }}>{lastError}</p>}

      <Avatar3D
        isSpeacking={isSpeaking}
        audioRef={audioRef}
        visemes={visemes}
        avatarState={avatarState}
      />

      <p style={{ minHeight: "60px", maxWidth: "700px", textAlign: "center" }}>
        {avatarText}
      </p>

      {totalQuestions > 0 && (
        <p>
          Question {questionIndex} / {totalQuestions}
        </p>
      )}

      <p>
        Mic: {isRecording ? "on" : "off"} | AI:{" "}
        {avatarState === "thinking"
          ? "thinking..."
          : avatarState === "speaking"
            ? "speaking..."
            : "listening"}
      </p>

      {stage === "waiting_resume" && (
        <label>
          Upload Resume:
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => {
              if (e.target.files?.[0]) {
                uploadResume(e.target.files[0]);
              }
            }}
          />
        </label>
      )}

      {(stage === "asking_question" || stage === "listening") && (
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <button type="button" onClick={startAudioStream} disabled={isRecording}>
            Start Mic Stream
          </button>
          <button type="button" onClick={stopAudioStream} disabled={!isRecording}>
            Stop Mic Stream
          </button>
          <label>
            Upload (fallback):
            <input
              type="file"
              accept=".wav,.webm,.mp3"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  sendAudioAnswer(e.target.files[0]);
                }
              }}
            />
          </label>
        </div>
      )}

      {partialTranscript && (
        <pre
          style={{
            whiteSpace: "pre-wrap",
            maxWidth: "900px",
            background: "#eef3ff",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          {partialTranscript}
        </pre>
      )}

      {lastEvaluation && (
        <pre
          style={{
            whiteSpace: "pre-wrap",
            maxWidth: "900px",
            background: "#f2f2f2",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          {JSON.stringify(lastEvaluation, null, 2)}
        </pre>
      )}

      {stage === "completed" && finalReport && (
        <pre
          style={{
            whiteSpace: "pre-wrap",
            maxWidth: "900px",
            background: "#e9f5ee",
            padding: "1rem",
            borderRadius: "8px",
          }}
        >
          {JSON.stringify(finalReport, null, 2)}
        </pre>
      )}
    </div>
  );
}
