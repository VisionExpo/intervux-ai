import { useEffect, useRef, useState, useCallback, useReducer, useMemo } from "react";
import type { VisemeCue } from "../avatar/LipSyncController";
import { interviewReducer, initialState } from "./useInterviewStateMachine";
import type { InterviewState } from "./useInterviewStateMachine";

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

const WS_BASE_URL = `${import.meta.env.VITE_WS_URL ?? "ws://localhost:8000"}/ws/interview`;

/**
 * Build the WebSocket URL.
 *
 * Appends:
 *   ?token=<jwt>
 *   &mock_session_id=<id>   (if stored in sessionStorage)
 *
 * The frontend stores mock_session_id in sessionStorage when it calls
 * POST /api/candidate/mock-interview/start so the gateway can link this
 * WebSocket session back to the MockInterview DB row.
 */
function getWebSocketUrl(): string {
  const token = localStorage.getItem("auth_token") ?? "";
  const hash = window.location.hash ?? "";
  const hashQuery = hash.includes("?") ? hash.split("?", 2)[1] ?? "" : "";
  const hashParams = new URLSearchParams(hashQuery);
  const mockSessionIdFromHash = hashParams.get("mock_session_id") ?? "";
  const mockSessionId =
    mockSessionIdFromHash || sessionStorage.getItem("mock_session_id") || "";

  const params = new URLSearchParams();
  if (token) params.set("token", token);
  if (mockSessionId) {
    params.set("mock_session_id", mockSessionId);
    params.set("session_id", mockSessionId);
  }

  const qs = params.toString();
  return qs ? `${WS_BASE_URL}?${qs}` : WS_BASE_URL;
}

export function useInterview() {
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const connectIdRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const reconnectAttemptsRef = useRef(0);
  const inFlightSendRef = useRef(false);
  const socketInitialized = useRef(false);

  const [stage, dispatch] = useReducer(interviewReducer, initialState);
  const stageRef = useRef<InterviewState>(stage);

  const audioContextRef = useRef<AudioContext | null>(null);
  const audioSourceRef = useRef<AudioBufferSourceNode | null>(null);
  const playbackStartTimeRef = useRef<number>(0);
  const audioQueueRef = useRef<QueuedAudioChunk[]>([]);
  const pendingVisemesRef = useRef<VisemeCue[] | null>(null);
  const isPlayingQueueRef = useRef(false);
  const nextExpectedSeqRef = useRef(1);
  const incomingBufferRef = useRef<Map<number, any>>(new Map());
  const bufferTimeoutRef = useRef<number | null>(null);
  const heartbeatIntervalRef = useRef<any>(null);
  const streamEndTimerRef = useRef<number | null>(null);

  const [avatarText, setAvatarText] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluationPayload | null>(null);
  const [partialTranscript, setPartialTranscript] = useState("");
  const [finalReport, setFinalReport] = useState<Record<string, unknown> | null>(null);
  const [lastError, setLastError] = useState<string>("");
  const visemesRef = useRef<VisemeCue[]>([]);
  const [emotion, setEmotion] = useState("neutral");
  const [transcriptMessages, setTranscriptMessages] = useState<TranscriptMessage[]>([]);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const isRecordingRef = useRef(false);

  const avatarState: AvatarState = useMemo(() => {
    if (isSpeaking) return "speaking";
    if (stage === "LISTENING") return "listening";
    if (
      stage === "PROCESSING_RESUME" ||
      stage === "PROCESSING_ANSWER" ||
      stage === "CONNECTING"
    ) {
      return "thinking";
    }
    return "thinking";
  }, [isSpeaking, stage]);

  const addTranscriptMessage = useCallback((speaker: "ai" | "candidate", text: string) => {
    const newMessage: TranscriptMessage = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      speaker,
      text,
      timestamp: new Date(),
    };
    setTranscriptMessages((prev) => [...prev, newMessage]);
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscriptMessages([]);
  }, []);

  useEffect(() => {
    stageRef.current = stage;

    // Stuck stage watchdog
    const stuckStages: InterviewState[] = ["PROCESSING_RESUME", "PROCESSING_ANSWER"];
    if (stuckStages.includes(stage)) {
      const timer = window.setTimeout(() => {
        console.warn(`Watchdog: Stuck in ${stage} for too long.`);
        setLastError("Processing is taking longer than expected. Please wait.");
      }, 15000);
      return () => window.clearTimeout(timer);
    }
  }, [stage]);

  // Initialization of continuous media stream
  useEffect(() => {
    let activeStream: MediaStream | null = null;
    async function initContinuousStream() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        activeStream = stream;
        mediaStreamRef.current = stream;
        setMediaStream(stream);
      } catch (err) {
        console.error("Failed to acquire continuous media stream:", err);
        setLastError("Microphone/Camera access blocked. Please allow browser permissions.");
      }
    }
    void initContinuousStream();

    return () => {
      if (activeStream) {
        activeStream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);


  useEffect(() => {
    if (socketInitialized.current) return;
    socketInitialized.current = true;
    connectSocket();

    return () => {
      console.warn("[WS] owner cleanup", {
        phase: stageRef.current,
        readyState: socketRef.current?.readyState,
      });
      shouldReconnectRef.current = false;
      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      if (streamEndTimerRef.current !== null) {
        window.clearTimeout(streamEndTimerRef.current);
        streamEndTimerRef.current = null;
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      // Note: The global mediaStream cleanup is handled by the dedicated useEffect.
      interruptAudio();
      socketRef.current?.close(1000, "Interview session provider unmounted");
      socketInitialized.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const processMessage = useCallback((msg: any) => {
    const type = typeof msg.type === "string" ? msg.type : "";
    const normalizedType = type.toLowerCase();

    if (type === "PHASE_CHANGE") {
      const phase = msg.phase as InterviewState;
      let mappedPhase = phase;
      if (phase as any === "QUESTION") mappedPhase = "ASKING_QUESTION";
      if (phase as any === "PROCESSING") mappedPhase = "PROCESSING_ANSWER";
      if (phase as any === "COMPLETE") mappedPhase = "INTERVIEW_COMPLETE";
      
      dispatch({ type: "SET_PHASE", phase: mappedPhase });
      
      if (mappedPhase === "LISTENING" || mappedPhase === "INTERVIEW_COMPLETE") {
        interruptAudio();
      }
      return;
    }

    if (type === "RESUMED") {
      const phase = msg.phase as InterviewState;
      let mappedPhase = phase;
      if (phase as any === "QUESTION") mappedPhase = "ASKING_QUESTION";
      if (phase as any === "PROCESSING") mappedPhase = "PROCESSING_ANSWER";
      if (phase as any === "COMPLETE") mappedPhase = "INTERVIEW_COMPLETE";

      if (typeof msg.next_seq === "number" && msg.next_seq > 0) {
        nextExpectedSeqRef.current = msg.next_seq;
        incomingBufferRef.current.clear();
      }
      dispatch({ type: "SET_PHASE", phase: mappedPhase });
      return;
    }

    if (type === "avatar_sync" || type === "question" || type === "next_question") {
      const text = typeof msg.text === "string" ? msg.text : "";
      const qIndex = Number(msg.question_index ?? 0);

      setAvatarText(text);
      setQuestionIndex(qIndex);
      setTotalQuestions(Number(msg.total_questions ?? 0));

      if (text && qIndex > 0) {
        addTranscriptMessage("ai", text);
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
      if (data?.transcript) {
        addTranscriptMessage("candidate", data.transcript);
      }
      setPartialTranscript("");
      return;
    }

    if (type === "interview_complete" || normalizedType === "complete") {
      setFinalReport((msg.report ?? null) as Record<string, unknown> | null);
      dispatch({ type: "SET_PHASE", phase: "INTERVIEW_COMPLETE" });
      shouldReconnectRef.current = false;
      sessionStorage.removeItem("mock_session_id");
      return;
    }

    if (type === "ERROR" || normalizedType === "error") {
      const message = typeof msg.message === "string" ? msg.message : "Server error.";
      setLastError(message);
      dispatch({ type: "ERROR_OCCURRED" });
      if (msg.recoverable === false) {
        shouldReconnectRef.current = false;
      }
      return;
    }

    if (type === "system_message") {
      const text = typeof msg.text === "string" ? msg.text : "";
      if (text) {
        setLastError(text);
      }
      return;
    }

    if (type === "partial_transcript") {
      const text = typeof msg.text === "string" ? msg.text : "";
      setPartialTranscript(text);
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
  }, [
    addTranscriptMessage,
    dispatch,
    setAvatarText,
    setQuestionIndex,
    setTotalQuestions,
    setEmotion,
    setLastEvaluation,
    setPartialTranscript,
    setTranscriptMessages,
    setFinalReport,
    setLastError,
  ]);

  const flushBuffer = useCallback(() => {
    const hasHigherSeqAvailable = () => {
      const keys = Array.from(incomingBufferRef.current.keys());
      return keys.some(k => k > nextExpectedSeqRef.current);
    };

    while (!incomingBufferRef.current.has(nextExpectedSeqRef.current) && hasHigherSeqAvailable()) {
      console.warn(`Skipping missing seq: ${nextExpectedSeqRef.current}`);
      nextExpectedSeqRef.current++;
    }

    while (incomingBufferRef.current.has(nextExpectedSeqRef.current)) {
      const bufferedMsg = incomingBufferRef.current.get(nextExpectedSeqRef.current);
      incomingBufferRef.current.delete(nextExpectedSeqRef.current);
      processMessage(bufferedMsg);
      nextExpectedSeqRef.current++;
    }
    bufferTimeoutRef.current = null;
  }, [processMessage]);

  function connectSocket() {
    console.log("WS CONNECT", getWebSocketUrl());
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (bufferTimeoutRef.current !== null) {
      window.clearTimeout(bufferTimeoutRef.current);
      bufferTimeoutRef.current = null;
    }
    nextExpectedSeqRef.current = 1;
    incomingBufferRef.current.clear();

    connectIdRef.current += 1;
    const connectId = connectIdRef.current;
    dispatch({ type: "WS_CONNECTING" });

    if (socketRef.current) {
      console.log("Cleaning up existing WebSocket before new connection...");
      // Remove handlers before closing to prevent race-induced reconnects
      socketRef.current.onopen = null;
      socketRef.current.onmessage = null;
      socketRef.current.onerror = null;
      socketRef.current.onclose = null;
      socketRef.current.close(1000, "Replacing stale interview socket");
      socketRef.current = null;
    }

    const ws = new WebSocket(getWebSocketUrl());
    ws.binaryType = "arraybuffer";
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected successfully (connectId:", connectId, ")");
      if (connectId !== connectIdRef.current) return;
      reconnectAttemptsRef.current = 0;
      setIsConnected(true);
      setLastError("");
      dispatch({ type: "WS_CONNECTED" });

      // Start heartbeat to prevent timeouts
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping", version: "v1" }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      if (connectId !== connectIdRef.current) return;

      if (event.data instanceof ArrayBuffer) {
        enqueueAudioChunk(event.data);
        return;
      }

      if (typeof event.data !== "string") return;

      let msg: any;
      try {
        msg = JSON.parse(event.data);
      } catch {
        setLastError("Received invalid JSON from server.");
        dispatch({ type: "ERROR_OCCURRED" });
        return;
      }

      if (msg.type === "RESUMED") {
        processMessage(msg);
        return;
      }

      // Monotonic sequence handling
      if (typeof msg.seq === "number") {
        if (msg.seq === nextExpectedSeqRef.current) {
          processMessage(msg);
          nextExpectedSeqRef.current++;
          
          // Drain buffer
          while (incomingBufferRef.current.has(nextExpectedSeqRef.current)) {
            const bufferedMsg = incomingBufferRef.current.get(nextExpectedSeqRef.current);
            incomingBufferRef.current.delete(nextExpectedSeqRef.current);
            processMessage(bufferedMsg);
            nextExpectedSeqRef.current++;
          }
          
          if (bufferTimeoutRef.current) {
            window.clearTimeout(bufferTimeoutRef.current);
            bufferTimeoutRef.current = null;
          }
        } else if (msg.seq > nextExpectedSeqRef.current) {
          console.warn(`Out of order: expected ${nextExpectedSeqRef.current}, got ${msg.seq}`);
          incomingBufferRef.current.set(msg.seq, msg);
          
          if (!bufferTimeoutRef.current) {
            bufferTimeoutRef.current = window.setTimeout(() => {
              console.warn(`Sequence timeout for ${nextExpectedSeqRef.current}, recovery...`);
              flushBuffer();
            }, 2000);
          }
        }
        return;
      }

      // Fallback for non-sequenced messages
      processMessage(msg);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (connectId !== connectIdRef.current) return;
      setLastError("WebSocket error.");
      dispatch({ type: "ERROR_OCCURRED" });
    };

    ws.onclose = (event) => {
      console.warn("[WS] close", {
        code: event.code,
        reason: event.reason || "no reason",
        wasClean: event.wasClean,
        phase: stageRef.current,
        readyState: ws.readyState,
      });
      
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (connectId !== connectIdRef.current) {
        console.log("Ignoring onclose for stale connection ID:", connectId);
        return;
      }
      setIsConnected(false);

      const intentionalClose = event.code === 1000;
      const interviewComplete = stageRef.current === "INTERVIEW_COMPLETE";

      if (!shouldReconnectRef.current || intentionalClose || interviewComplete) return;

      if (reconnectAttemptsRef.current >= 5) {
        setLastError("Connection closed. Please refresh to continue.");
        dispatch({ type: "ERROR_OCCURRED" });
        return;
      }

      reconnectAttemptsRef.current += 1;
      const delayMs = Math.min(5000, 600 * reconnectAttemptsRef.current);
      setLastError("Connection interrupted. Reconnecting...");
      reconnectTimerRef.current = window.setTimeout(() => {
        if (!shouldReconnectRef.current || stageRef.current === "INTERVIEW_COMPLETE") return;
        connectSocket();
      }, delayMs);
    };
  }

  const uploadResume = useCallback(async (file: File) => {
    if (stageRef.current !== "WAITING_RESUME") {
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
      // dispatch({ type: "RESUME_UPLOAD_START" }); // REMOVED: Now driven by backend PHASE_CHANGE
      const fileBytes = await fileToBase64(file);
      socketRef.current.send(
        JSON.stringify({
          type: "resume_upload",
          version: "v1",
          file_name: file.name,
          file_bytes: fileBytes,
        })
      );
      setLastError("");
    } finally {
      inFlightSendRef.current = false;
    }
  }, [dispatch]);

  const startAudioStream = useCallback(async () => {
    if (stageRef.current !== "LISTENING") {
      console.warn("Cannot start audio stream outside of LISTENING stage");
      return;
    }
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setLastError("Socket is not connected.");
      dispatch({ type: "ERROR_OCCURRED" });
      return;
    }
    if (isRecordingRef.current) {
      console.log("Audio stream already recording, skipping start.");
      return;
    }

    const stream = mediaStreamRef.current;
    if (!stream) {
      setLastError("Media stream is not available.");
      dispatch({ type: "ERROR_OCCURRED" });
      return;
    }

    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : "audio/webm";

    const recorder = new MediaRecorder(stream, { mimeType });
    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = async (event) => {
      if (stageRef.current !== "LISTENING") return;
      if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
      if (event.data.size <= 0) return;
      const buffer = await event.data.arrayBuffer();
      socketRef.current.send(buffer);
    };

    recorder.onstop = () => {
      if (streamEndTimerRef.current !== null) {
        window.clearTimeout(streamEndTimerRef.current);
        streamEndTimerRef.current = null;
      }
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: "stream_end", version: "v1" }));
        // dispatch({ type: "ANSWER_PROCESSING_START" }); // REMOVED: Now driven by backend PHASE_CHANGE
      }
      // DO NOT stop the tracks or nullify mediaStreamRef here!
      // This allows the continuous camera feed to persist.
      mediaRecorderRef.current = null;
      isRecordingRef.current = false;
      setIsRecording(false);
    };

    recorder.start(300);
    isRecordingRef.current = true;
    if (streamEndTimerRef.current !== null) {
      window.clearTimeout(streamEndTimerRef.current);
    }
    streamEndTimerRef.current = window.setTimeout(() => {
      if (stageRef.current !== "LISTENING") return;
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
    }, 90000);
    setIsRecording(true);
    setPartialTranscript("");
    setLastError("");
  }, [dispatch]);

  const stopAudioStream = useCallback(() => {
    if (streamEndTimerRef.current !== null) {
      window.clearTimeout(streamEndTimerRef.current);
      streamEndTimerRef.current = null;
    }
    const recorder = mediaRecorderRef.current;
    if (!recorder) {
      isRecordingRef.current = false;
      setIsRecording(false);
      return;
    }
    if (recorder.state !== "inactive") {
      recorder.stop();
    }
    isRecordingRef.current = false;
    setIsRecording(false);
  }, []);

  function enqueueAudioChunk(audio: ArrayBuffer) {
    const nextVisemes = pendingVisemesRef.current || [];
    pendingVisemesRef.current = null;

    // Safety limit: drop oldest if queue grows too large (prevents memory leaks/lag)
    if (audioQueueRef.current.length > 10) {
      console.warn("Audio queue overflow, dropping oldest chunk.");
      audioQueueRef.current.shift();
    }

    audioQueueRef.current.push({ audio, visemes: nextVisemes });
    void playNextQueuedAudio();
  }

  async function playNextQueuedAudio() {
    if (isPlayingQueueRef.current) return;

    const next = audioQueueRef.current.shift();
    if (!next) {
      isPlayingQueueRef.current = false;
      setIsSpeaking(false);
      visemesRef.current = [];
      return;
    }

    // Initialize or resume AudioContext
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    const ctx = audioContextRef.current;
    
    if (ctx.state === "suspended") {
      await ctx.resume();
    }

    isPlayingQueueRef.current = true;
    setIsSpeaking(true);
    visemesRef.current = next.visemes;

    try {
      // Decode the ArrayBuffer into an AudioBuffer
      // Note: We use slice(0) to avoid detached buffer issues if the original buffer is reused
      const audioBuffer = await ctx.decodeAudioData(next.audio.slice(0));
      
      const source = ctx.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(ctx.destination);
      
      audioSourceRef.current = source;
      playbackStartTimeRef.current = ctx.currentTime;
      
      source.onended = () => {
        console.log("Audio ended");
        audioSourceRef.current = null;
        isPlayingQueueRef.current = false;
        // Small delay to allow state to settle before next chunk
        setTimeout(() => {
          void playNextQueuedAudio();
        }, 10);
      };
      
      console.log("Audio started");
      source.start(0);
    } catch (err) {
      console.error("Audio playback error:", err);
      isPlayingQueueRef.current = false;
      void playNextQueuedAudio();
    }
  }

  const interruptAudio = useCallback(() => {
    audioQueueRef.current = [];
    pendingVisemesRef.current = null;
    isPlayingQueueRef.current = false;
    setIsSpeaking(false);
    visemesRef.current = [];

    if (audioSourceRef.current) {
      try {
        audioSourceRef.current.stop();
      } catch (err) {
        // Source might already be stopped or not started
      }
      audioSourceRef.current = null;
    }
  }, []);


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
      audioContextRef,
      playbackStartTimeRef,
      visemesRef,
      emotion,
      transcriptMessages,
      mediaStream,
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

      return { start, end, viseme } satisfies VisemeCue;
    })
    .filter((item): item is VisemeCue => item !== null);
}
