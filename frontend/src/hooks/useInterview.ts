import { useEffect, useRef, useState, useCallback, useReducer } from "react";
import type { VisemeCue } from "../avatar/LipSyncController";
import {
  interviewReducer,
  initialState,
  InterviewState,
} from "./useInterviewStateMachine";

export type AvatarState = "speaking" | "listening" | "thinking";

export type EvaluationPayload = {
  question_index: number;
  question: string;
  transcript: string;
  evaluation: Record<string, unknown>;
};

export type TranscriptMessage = {
  id: string;
  speaker: "ai" | "candidate";
  text: string;
  timestamp?: Date;
};

type QueuedAudioChunk = {
  audio: ArrayBuffer;
  visemes: VisemeCue[];
};

const WS_URL = "ws://localhost:8000/ws/interview";
const MAX_RECONNECT_ATTEMPTS = 6;

function getWebSocketUrl(): string {
  const token = localStorage.getItem("auth_token");
  if (token) {
    return `${WS_URL}?token=${encodeURIComponent(token)}`;
  }
  return WS_URL;
}

export function useInterview() {
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const connectIdRef = useRef(0);
  const reconnectAttemptRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const inFlightSendRef = useRef(false);
  const socketInitialized = useRef(false);
  
  const [stage, dispatch] = useReducer(interviewReducer, initialState);
  const stageRef = useRef<InterviewState>(stage);

  const audioRef = useRef<HTMLAudioElement | null>(new Audio());
  const activeObjectUrlRef = useRef<string | null>(null);
  const audioQueueRef = useRef<QueuedAudioChunk[]>([]);
  const pendingVisemesRef = useRef<VisemeCue[] | null>(null);
  const isPlayingQueueRef = useRef(false);

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
  const [emotion, setEmotion] = useState("neutral");
  const [transcriptMessages, setTranscriptMessages] = useState<TranscriptMessage[]>([]);

  // Add message to transcript
  const addTranscriptMessage = useCallback((speaker: "ai" | "candidate", text: string) => {
    const newMessage: TranscriptMessage = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      speaker,
      text,
      timestamp: new Date(),
    };
    setTranscriptMessages((prev) => [...prev, newMessage]);
  }, []);

  // Clear transcript
  const clearTranscript = useCallback(() => {
    setTranscriptMessages([]);
  }, []);

  useEffect(() => {
    stageRef.current = stage;
  }, [stage]);

  useEffect(() => {
    if (socketInitialized.current) {
      return;
    }
    socketInitialized.current = true;
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
      socketInitialized.current = false;
    };
  }, []);

  function connectSocket() {
    connectIdRef.current += 1;
    const connectId = connectIdRef.current;
    dispatch({ type: "WS_CONNECTING" });
    setAvatarState("thinking");

    const ws = new WebSocket(getWebSocketUrl());
    ws.binaryType = "arraybuffer";
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected successfully");
      if (connectId !== connectIdRef.current) return;
      reconnectAttemptRef.current = 0;
      setIsConnected(true);
      setLastError("");
      dispatch({ type: "WS_CONNECTED" });
    };

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
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
        dispatch({ type: "ERROR_OCCURRED" });
        return;
      }

      const type = typeof msg.type === "string" ? msg.type : "";

      if (type === "avatar_sync" || type === "question" || type === "next_question") {
        const text = typeof msg.text === "string" ? msg.text : "";
        const qIndex = Number(msg.question_index ?? 0);
        
        setAvatarText(text);
        setQuestionIndex(qIndex);
        setTotalQuestions(Number(msg.total_questions ?? 0));
        
        if (text && qIndex > 0) {
          addTranscriptMessage("ai", text);
        }
        
        if (qIndex === 1 && stageRef.current === 'PROCESSING_RESUME') {
            dispatch({ type: "RESUME_PROCESS_SUCCESS" });
        } else if (qIndex > 0) {
            dispatch({ type: "QUESTION_RECEIVED" });
        }
        return;
      }

      if (type === "avatar_visemes") {
        pendingVisemesRef.current = parseVisemes(msg.visemes);
        return;
      }

      if (type === "emotion_update") {
        setEmotion(typeof msg.emotion === "string" ? msg.emotion : "neutral");
        return;
      }

      if (type === "evaluation") {
        const data = (msg.data ?? null) as EvaluationPayload | null;
        setLastEvaluation(data);
        // Add candidate's answer to transcript
        if (data?.transcript) {
          addTranscriptMessage("candidate", data.transcript);
        }
        setPartialTranscript("");
        dispatch({ type: "EVALUATION_COMPLETE" });
        setAvatarState("thinking");
        return;
      }

      if (type === "interview_complete") {
        setFinalReport((msg.report ?? null) as Record<string, unknown> | null);
        dispatch({ type: "INTERVIEW_COMPLETE" });
        setAvatarState("listening");
        shouldReconnectRef.current = false;
        return;
      }

      if (type === "error") {
        const message =
          typeof msg.message === "string" ? msg.message : "Server error.";
        setLastError(message);
        dispatch({ type: "ERROR_OCCURRED" });
        return;
      }

      if (type === "server_shutdown") {
        const message =
          typeof msg.message === "string"
            ? msg.message
            : "Server is restarting. Reconnecting...";
        setLastError(message);
        dispatch({ type: "RESET" });
        return;
      }

      if (type === "partial_transcript") {
        const text = typeof msg.text === "string" ? msg.text : "";
        setPartialTranscript(text);
        // Update the last candidate message with partial transcript
        setTranscriptMessages((prev) => {
          const lastMsg = prev[prev.length - 1];
          if (lastMsg && lastMsg.speaker === "candidate") {
            const updated = [...prev];
            updated[updated.length - 1] = { ...lastMsg, text };
            return updated;
          }
          return prev;
        });
        return;
      }

      if (type === "phase") {
        const value = typeof msg.value === "string" ? msg.value : "";
        if (value === "LISTENING") {
          dispatch({ type: "PHASE_LISTENING" });
          if (!isPlayingQueueRef.current) setAvatarState("listening");
        } else if (value === "PROCESSING") {
          dispatch({ type: "ANSWER_PROCESSING_START" });
          if (!isPlayingQueueRef.current) setAvatarState("thinking");
        }
        return;
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (connectId !== connectIdRef.current) return;
      setLastError("WebSocket error.");
      dispatch({ type: "ERROR_OCCURRED" });
    };

    ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      if (connectId !== connectIdRef.current) return;
      setIsConnected(false);

      if (!shouldReconnectRef.current) return;
      if (stageRef.current === "INTERVIEW_COMPLETE") return;

      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    const attempt = reconnectAttemptRef.current + 1;
    reconnectAttemptRef.current = attempt;

    if (attempt > MAX_RECONNECT_ATTEMPTS) {
      setLastError("Connection lost. Max reconnect attempts reached.");
      dispatch({ type: "ERROR_OCCURRED" });
      return;
    }

    const backoffMs = Math.min(1500 * 2 ** (attempt - 1), 15000);
    const jitterMs = Math.floor(Math.random() * 300);
    const delayMs = backoffMs + jitterMs;
    setLastError(`Connection lost. Reconnecting (attempt ${attempt})...`);
    dispatch({ type: "RESET" });
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
    if (stage !== 'WAITING_RESUME') {
      console.warn("Cannot upload resume outside of WAITING_RESUME stage");
      return;
    }
    if (inFlightSendRef.current) return;
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      dispatch({ type: "ERROR_OCCURRED" });
      return;
    }

    inFlightSendRef.current = true;
    try {
      dispatch({ type: "RESUME_UPLOAD_START" });
      const fileBytes = await fileToBase64(file);
      socketRef.current.send(
        JSON.stringify({
          type: "resume_upload",
          file_name: file.name,
          file_bytes: fileBytes,
        })
      );
      setAvatarState("thinking");
      setLastError("");
    } finally {
      inFlightSendRef.current = false;
    }
  }

  async function startAudioStream() {
    if (stage !== 'LISTENING') {
      console.warn("Cannot start audio stream outside of LISTENING stage");
      return;
    }
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      dispatch({ type: "ERROR_OCCURRED" });
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
      if (stageRef.current !== 'LISTENING') return;
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
        dispatch({ type: "ANSWER_PROCESSING_START" });
      }
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
      mediaRecorderRef.current = null;
      setIsRecording(false);
      if (!isPlayingQueueRef.current) setAvatarState("thinking");
    };

    recorder.start(300);
    setPartialTranscript("");
    setIsRecording(true);
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
      setAvatarState(stageRef.current === "PROCESSING_ANSWER" ? "thinking" : "listening");
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
    emotion,
    transcriptMessages,
    addTranscriptMessage,
    clearTranscript,
    uploadResume,
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
