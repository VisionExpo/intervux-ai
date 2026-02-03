import { useAvatarSocket } from "../hooks/useAvatarSocket";

export default function InterviewPage() {
    const { avatarText } = useAvatarSocket();

    return (
        <div style={{ padding: "2rem" }}>
            <h2>Interviewer</h2>
            <p>{avatarText || "Waiting for interviewer..."</p>
        </div>
    );
}