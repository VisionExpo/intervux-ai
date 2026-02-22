import Avatar3D from "../components/Avatar3D";
import { useInterview } from "../hooks/useInterview";

export default function InterviewPage() {
  const {
    avatarText,
    isSpeaking,
    stage,
    startInterview,
    uploadResume,
    generateQuestions,
    getQuestion
  } = useInterview();

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "2rem",
      fontFamily: "Arial"
    }}>
      <h1>Intervux AI – Voice Interview</h1>

      <Avatar3D isSpeacking={isSpeaking} />

      <p style={{ marginTop: "1rem", minHeight: "60px" }}>
        {avatarText || "Start your interview to begin."}
      </p>

      <div style={{
        marginTop: "2rem",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        width: "300px"
      }}>

        <button
          onClick={startInterview}
          disabled={stage !== "idle"}
        >
          Start Interview
        </button>

        {stage === "started" && (
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => {
              if (e.target.files) {
                uploadResume(e.target.files[0]);
              }
            }}
          />
        )}

        {stage === "resume_uploaded" && (
          <button onClick={generateQuestions}>
            Generate Questions
          </button>
        )}

        {stage === "questions_ready" && (
          <button onClick={getQuestion}>
            Ask Question
          </button>
        )}

      </div>
    </div>
  );
}