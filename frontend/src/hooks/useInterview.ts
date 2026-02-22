import { useState } from "react";

export function useInterview() {
  const [avatarText, setAvatarText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [stage, setStage] = useState("idle");

  async function startInterview() {
    await fetch("http://localhost:8000/start", {
      method: "POST"
    });
    setStage("started");
  }

  async function uploadResume(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    await fetch("http://localhost:8000/upload-resume", {
      method: "POST",
      body: formData
    });

    setStage("resume_uploaded");
  }

  async function generateQuestions() {
    await fetch("http://localhost:8000/generate-questions", {
      method: "POST"
    });

    setStage("questions_ready");
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
    stage,
    startInterview,
    uploadResume,
    generateQuestions,
    getQuestion
  };
}