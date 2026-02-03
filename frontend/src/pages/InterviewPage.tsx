import { useAvatarSocket } from "../hooks/useAvatarSocket";
import Avatar3D from "../components/Avatar3D";


export default function InterviewPage() {
  const { avatarText, isSpeaking } = useAvatarSocket();

  return (
    <div style={{ padding: "2rem" }}>
      <Avatar3D isSpeacking={isSpeaking} />
      <h2>Interviewer</h2>
      <p>{avatarText || "Waiting..."}</p>
    </div>
  );
}
