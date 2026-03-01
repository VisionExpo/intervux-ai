import { useEffect, useRef, useState } from "react";

type InterviewStage =
  | "connecting"
  | "waiting_resume"
  | "asking_question"
  | "listening"
  | "processing"
  | "completed";

type EvaluationPayload = {
  question_index: number;
  question: string;
  transcript: string;
  evaluation: Record<string, unknown>;
};

export function useInterview() {
  const socketRef = useRef<WebSocket | null>(null);

  const [stage, setStage] = useState<InterviewStage>("connecting");
  const [avatarText, setAvatarText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluationPayload | null>(
    null
  );
  const [finalReport, setFinalReport] = useState<Record<string, unknown> | null>(
    null
  );

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/interview");
    ws.binaryType = "arraybuffer";
    socketRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setStage("waiting_resume");
    };

    ws.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        playAudio(event.data, setIsSpeaking);
        return;
      }

      if (typeof event.data !== "string") return;
      const msg = JSON.parse(event.data);

      if (msg.type === "avatar_sync") {
        setAvatarText(msg.text ?? "");
        setQuestionIndex(msg.question_index ?? 0);
        setTotalQuestions(msg.total_questions ?? 0);
        setStage(msg.question_index > 0 ? "asking_question" : "waiting_resume");
      }

      if (msg.type === "evaluation") {
        setLastEvaluation(msg.data ?? null);
        setStage("processing");
      }

      if (msg.type === "interview_complete") {
        setFinalReport(msg.report ?? null);
        setStage("completed");
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  async function uploadResume(file: File) {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;

    const fileBytes = await fileToBase64(file);
    socketRef.current.send(
      JSON.stringify({
        type: "resume_upload",
        file_name: file.name,
        file_bytes: fileBytes,
      })
    );
    setStage("processing");
  }

  async function sendAudioAnswer(file: File) {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;

    setStage("listening");
    const buffer = await file.arrayBuffer();
    socketRef.current.send(buffer);
    setStage("processing");
  }

  return {
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
  };
}

async function fileToBase64(file: File): Promise<string> {
  const dataUrl = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

  const [, base64] = dataUrl.split(",", 2);
  return base64 ?? "";
}

function playAudio(buffer: ArrayBuffer, setIsSpeaking: (v: boolean) => void) {
  const blob = new Blob([buffer], { type: "audio/wav" });
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);

  setIsSpeaking(true);
  audio.play().catch(() => setIsSpeaking(false));
  audio.onended = () => {
    setIsSpeaking(false);
    URL.revokeObjectURL(url);
  };
}
