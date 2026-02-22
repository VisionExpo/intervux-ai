import { useState } from "react";

export function useInterview() {
  const [avatarText, setAvatarText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);

  async function startInterview() {
    await fetch("http://localhost:8000/start", {
      method: "POST"
    });
  }

  async function getQuestion() {
    const res = await fetch("http://localhost:8000/question");
    const data = await res.json();

    setAvatarText(data.question_text);

    if (data.question_audio_url) {
      const audio = new Audio(
        "http://localhost:8000" + data.question_audio_url
      );
      setIsSpeaking(true);
      audio.play();
      audio.onended = () => setIsSpeaking(false);
    }
  }

  return {
    avatarText,
    isSpeaking,
    startInterview,
    getQuestion,
  };
}