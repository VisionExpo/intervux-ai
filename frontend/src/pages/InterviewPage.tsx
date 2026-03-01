import Avatar3D from "../components/Avatar3D";
import { useInterview } from "../hooks/useInterview";

export default function InterviewPage() {
  const {
    stage,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    lastEvaluation,
    finalReport,
    uploadResume,
    sendAudioAnswer,
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

      <Avatar3D isSpeacking={isSpeaking} />

      <p style={{ minHeight: "60px", maxWidth: "700px", textAlign: "center" }}>
        {avatarText}
      </p>

      {totalQuestions > 0 && (
        <p>
          Question {questionIndex} / {totalQuestions}
        </p>
      )}

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

      {stage === "asking_question" && (
        <label>
          Upload Answer Audio (wav/webm):
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
