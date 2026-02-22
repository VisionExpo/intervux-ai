import Avatar3D from "../components/Avatar3D";
import { useInterview } from "../hooks/useInterview";

export default function InterviewPage() {
  const {
    avatarText,
    isSpeaking,
    startInterview,
    getQuestion
  } = useInterview();

  return (
    <div style={{ padding: "2rem" }}>
      <Avatar3D isSpeacking={isSpeaking} />

      <h2>Interviewer</h2>
      <p>{avatarText || "Click Start to Begin"}</p>

      <button onClick={startInterview}>
        Start Interview
      </button>

      <button onClick={getQuestion}>
        Ask Question
      </button>
    </div>
  );
}