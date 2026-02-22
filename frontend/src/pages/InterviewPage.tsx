import { useState } from "react";

export default function InterviewPage() {
  const [question, setQuestion] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [evaluation, setEvaluation] = useState<any>(null);

  async function startInterview() {
    await fetch("http://localhost:8000/start", {
      method: "POST"
    });
  }

  async function getQuestion() {
    const res = await fetch("http://localhost:8000/question");
    const data = await res.json();
    setQuestion(data.question_text);
    setAudioUrl(`http://localhost:8000${data.question_audio_url}`);
  }

  async function submitAnswer(file: File) {
    const formData = new FormData();
    formData.append("audio", file);

    const res = await fetch("http://localhost:8000/answer", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setEvaluation(data.evaluation);
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Intervux AI Demo</h1>

      <button onClick={startInterview}>Start Interview</button>
      <button onClick={getQuestion}>Get Question</button>

      <h3>{question}</h3>
      {audioUrl && <audio src={audioUrl} controls autoPlay />}

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => {
          if (e.target.files) {
            submitAnswer(e.target.files[0]);
          }
        }}
      />

      {evaluation && (
        <pre>{JSON.stringify(evaluation, null, 2)}</pre>
      )}
    </div>
  );
}