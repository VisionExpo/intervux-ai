import { useEffect, useRef, useState } from "react";
import type { VisemeCue } from "../avatar/LipSyncController";

type InterviewStage =
  | "connecting"
  | "waiting_resume"
  | "asking_question"
  | "listening"
  | "processing"
  | "completed";

type AvatarState = "speaking" | "listening" | "thinking";

type EvaluationPayload = {
  question_index: number;
  question: string;
  transcript: string;
  evaluation: Record<string, unknown>;
};

type QueuedAudioChunk = {
  audio: ArrayBuffer;
  visemes: VisemeCue[];
};

const WS_URL = "ws://localhost:8000/ws/interview";
const MAX_RECONNECT_ATTEMPTS = 6;

export function useInterview() {
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const connectIdRef = useRef(0);
  const reconnectAttemptRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const inFlightSendRef = useRef(false);
  const stageRef = useRef<InterviewStage>("connecting");

  const audioRef = useRef<HTMLAudioElement | null>(new Audio());
  const activeObjectUrlRef = useRef<string | null>(null);
  const audioQueueRef = useRef<QueuedAudioChunk[]>([]);
  const pendingVisemesRef = useRef<VisemeCue[] | null>(null);
  const isPlayingQueueRef = useRef(false);

  const [stage, setStage] = useState<InterviewStage>("connecting");
  const [avatarState, setAvatarState] = useState<AvatarState>("thinking");
  const [avatarText, setAvatarText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluationPayload | null>(
    null
  );
  const [partialTranscript, setPartialTranscript] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [finalReport, setFinalReport] = useState<Record<string, unknown> | null>(
    null
  );
  const [lastError, setLastError] = useState<string>("");
  const [visemes, setVisemes] = useState<VisemeCue[]>([]);

  useEffect(() => {
    stageRef.current = stage;
  }, [stage]);

  useEffect(() => {
    connectSocket();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      clearAudioQueue();
      socketRef.current?.close(1000, "Component unmounted");
    };
  }, []);

  function connectSocket() {
    connectIdRef.current += 1;
    const connectId = connectIdRef.current;
    setStage("connecting");
    setAvatarState("thinking");

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
        enqueueAudioChunk(event.data);
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

      if (type === "avatar_visemes") {
        pendingVisemesRef.current = parseVisemes(msg.visemes);
        return;
      }

      if (type === "evaluation") {
        const data = (msg.data ?? null) as EvaluationPayload | null;
        setLastEvaluation(data);
        setPartialTranscript("");
        setStage("asking_question");
        setAvatarState("thinking");
        return;
      }

      if (type === "interview_complete") {
        setFinalReport((msg.report ?? null) as Record<string, unknown> | null);
        setStage("completed");
        setAvatarState("listening");
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
          setAvatarState("thinking");
        }
        return;
      }

      if (type === "server_shutdown") {
        const message =
          typeof msg.message === "string"
            ? msg.message
            : "Server is restarting. Reconnecting...";
        setLastError(message);
        setStage("connecting");
        setAvatarState("thinking");
        return;
      }

      if (type === "partial_transcript") {
        setPartialTranscript(typeof msg.text === "string" ? msg.text : "");
        return;
      }

      if (type === "phase") {
        const value = typeof msg.value === "string" ? msg.value : "";
        if (value === "LISTENING") {
          setStage("listening");
          if (!isPlayingQueueRef.current) setAvatarState("listening");
        } else if (value === "PROCESSING") {
          setStage("processing");
          if (!isPlayingQueueRef.current) setAvatarState("thinking");
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
      if (stageRef.current === "completed") return;

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
    setAvatarState("thinking");

    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
    }
    reconnectTimerRef.current = window.setTimeout(() => {
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
      setAvatarState("thinking");
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
      setAvatarState("listening");
      const buffer = await file.arrayBuffer();
      socketRef.current.send(buffer);
      setStage("processing");
      setAvatarState("thinking");
      setLastError("");
    } finally {
      inFlightSendRef.current = false;
    }
  }

  async function startAudioStream() {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      return;
    }
    if (isRecording) return;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStreamRef.current = stream;

    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "audio/webm";

    const recorder = new MediaRecorder(stream, { mimeType });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = async (event) => {
      if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
        return;
      }
      if (event.data.size <= 0) return;
      const buffer = await event.data.arrayBuffer();
      socketRef.current.send(buffer);
    };

    recorder.onstop = () => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: "stream_end" }));
      }
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
      mediaRecorderRef.current = null;
      setIsRecording(false);
      setStage("processing");
      if (!isPlayingQueueRef.current) setAvatarState("thinking");
    };

    recorder.start(300);
    setPartialTranscript("");
    setIsRecording(true);
    setStage("listening");
    setAvatarState("listening");
    setLastError("");
  }

  function stopAudioStream() {
    const recorder = mediaRecorderRef.current;
    if (!recorder) return;
    if (recorder.state !== "inactive") {
      recorder.stop();
    }
  }

  function enqueueAudioChunk(audio: ArrayBuffer) {
    const nextVisemes = pendingVisemesRef.current ?? [];
    pendingVisemesRef.current = null;

    audioQueueRef.current.push({ audio, visemes: nextVisemes });
    void playNextQueuedAudio();
  }

  async function playNextQueuedAudio() {
    if (isPlayingQueueRef.current) return;

    const next = audioQueueRef.current.shift();
    if (!next) {
      setIsSpeaking(false);
      setVisemes([]);
      setAvatarState(stageRef.current === "processing" ? "thinking" : "listening");
      return;
    }

    const audioEl = audioRef.current;
    if (!audioEl) {
      setIsSpeaking(false);
      return;
    }

    isPlayingQueueRef.current = true;
    setIsSpeaking(true);
    setAvatarState("speaking");
    setVisemes(next.visemes);

    if (activeObjectUrlRef.current) {
      URL.revokeObjectURL(activeObjectUrlRef.current);
      activeObjectUrlRef.current = null;
    }

    const blob = new Blob([next.audio], { type: "audio/wav" });
    const objectUrl = URL.createObjectURL(blob);
    activeObjectUrlRef.current = objectUrl;

    audioEl.src = objectUrl;
    audioEl.currentTime = 0;

    const continueQueue = () => {
      audioEl.onended = null;
      audioEl.onerror = null;
      isPlayingQueueRef.current = false;
      setIsSpeaking(false);
      if (activeObjectUrlRef.current) {
        URL.revokeObjectURL(activeObjectUrlRef.current);
        activeObjectUrlRef.current = null;
      }
      void playNextQueuedAudio();
    };

    audioEl.onended = continueQueue;
    audioEl.onerror = continueQueue;

    try {
      await audioEl.play();
    } catch {
      continueQueue();
    }
  }

  function clearAudioQueue() {
    audioQueueRef.current = [];
    pendingVisemesRef.current = null;

    const audioEl = audioRef.current;
    if (audioEl) {
      audioEl.pause();
      audioEl.onended = null;
      audioEl.onerror = null;
      audioEl.removeAttribute("src");
      audioEl.load();
    }

    if (activeObjectUrlRef.current) {
      URL.revokeObjectURL(activeObjectUrlRef.current);
      activeObjectUrlRef.current = null;
    }

    isPlayingQueueRef.current = false;
    setIsSpeaking(false);
    setVisemes([]);
  }

  return {
    stage,
    avatarState,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    partialTranscript,
    isRecording,
    lastEvaluation,
    finalReport,
    lastError,
    audioRef,
    visemes,
    uploadResume,
    sendAudioAnswer,
    startAudioStream,
    stopAudioStream,
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

function parseVisemes(raw: unknown): VisemeCue[] {
  if (!Array.isArray(raw)) return [];

  return raw
    .map((item) => {
      if (!item || typeof item !== "object") return null;
      const record = item as Record<string, unknown>;

      const start = Number(record.start);
      const end = Number(record.end);
      const viseme = Number(record.viseme);

      if (!Number.isFinite(start) || !Number.isFinite(end) || !Number.isFinite(viseme)) {
        return null;
      }

      return {
        start,
        end,
        viseme,
      } satisfies VisemeCue;
    })
    .filter((item): item is VisemeCue => item !== null);
}
