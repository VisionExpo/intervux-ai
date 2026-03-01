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

const WS_URL = "ws://localhost:8000/ws/interview";
const MAX_RECONNECT_ATTEMPTS = 6;

export function useInterview() {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const connectIdRef = useRef(0);
  const reconnectAttemptRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const inFlightSendRef = useRef(false);

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
  const [lastError, setLastError] = useState<string>("");

  useEffect(() => {
    connectSocket();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      socketRef.current?.close(1000, "Component unmounted");
    };
  }, []);

  function connectSocket() {
    connectIdRef.current += 1;
    const connectId = connectIdRef.current;
    setStage("connecting");

    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";
    socketRef.current = ws;

    ws.onopen = () => {
      if (connectId !== connectIdRef.current) return;
      reconnectAttemptRef.current = 0;
      setIsConnected(true);
      setLastError("");
    };

    ws.onmessage = (event) => {
      if (connectId !== connectIdRef.current) return;

      if (event.data instanceof ArrayBuffer) {
        playAudio(event.data, setIsSpeaking);
        return;
      }

      if (typeof event.data !== "string") return;
      let msg: Record<string, unknown>;
      try {
        msg = JSON.parse(event.data);
      } catch {
        setLastError("Received invalid JSON from server.");
        return;
      }

      const type = typeof msg.type === "string" ? msg.type : "";

      if (type === "avatar_sync") {
        setAvatarText(typeof msg.text === "string" ? msg.text : "");
        setQuestionIndex(Number(msg.question_index ?? 0));
        setTotalQuestions(Number(msg.total_questions ?? 0));
        setStage(Number(msg.question_index ?? 0) > 0 ? "asking_question" : "waiting_resume");
        return;
      }

      if (type === "evaluation") {
        const data = (msg.data ?? null) as EvaluationPayload | null;
        setLastEvaluation(data);
        return;
      }

      if (type === "interview_complete") {
        setFinalReport((msg.report ?? null) as Record<string, unknown> | null);
        setStage("completed");
        shouldReconnectRef.current = false;
        return;
      }

      if (type === "error") {
        const message =
          typeof msg.message === "string" ? msg.message : "Server error.";
        setLastError(message);

        const recoverable = Boolean(msg.recoverable);
        if (!recoverable) {
          setStage("connecting");
        }
        return;
      }
    };

    ws.onerror = () => {
      if (connectId !== connectIdRef.current) return;
      setLastError("WebSocket error.");
    };

    ws.onclose = () => {
      if (connectId !== connectIdRef.current) return;
      setIsConnected(false);

      if (!shouldReconnectRef.current) return;
      if (stage === "completed") return;

      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    const attempt = reconnectAttemptRef.current + 1;
    reconnectAttemptRef.current = attempt;

    if (attempt > MAX_RECONNECT_ATTEMPTS) {
      setLastError("Connection lost. Max reconnect attempts reached.");
      return;
    }

    const backoffMs = Math.min(1500 * 2 ** (attempt - 1), 15000);
    const jitterMs = Math.floor(Math.random() * 300);
    const delayMs = backoffMs + jitterMs;
    setLastError(`Connection lost. Reconnecting (attempt ${attempt})...`);
    setStage("connecting");

    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
    }
    reconnectTimerRef.current = window.setTimeout(() => {
      // New socket means new server-side isolated session by design.
      setQuestionIndex(0);
      setTotalQuestions(0);
      setLastEvaluation(null);
      setAvatarText("Reconnected. Please upload resume again.");
      connectSocket();
    }, delayMs);
  }

  async function uploadResume(file: File) {
    if (inFlightSendRef.current) return;
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      return;
    }

    inFlightSendRef.current = true;
    try {
      const fileBytes = await fileToBase64(file);
      socketRef.current.send(
        JSON.stringify({
          type: "resume_upload",
          file_name: file.name,
          file_bytes: fileBytes,
        })
      );
      setStage("processing");
      setLastError("");
    } finally {
      inFlightSendRef.current = false;
    }
  }

  async function sendAudioAnswer(file: File) {
    if (inFlightSendRef.current) return;
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      return;
    }

    inFlightSendRef.current = true;
    try {
      setStage("listening");
      const buffer = await file.arrayBuffer();
      socketRef.current.send(buffer);
      setStage("processing");
      setLastError("");
    } finally {
      inFlightSendRef.current = false;
    }
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
    lastError,
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
