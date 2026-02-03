import { useEffect, useRef, useState } from "react";

export function useAvatarSocket() {
  const socketRef = useRef<WebSocket | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  const [avatarText, setAvatarText] = useState<string>("");

  useEffect(() => {
    // Setup AudioContext
    const audioCtx = new AudioContext();
    audioCtxRef.current = audioCtx;

    // Setup WebSocket
    const ws = new WebSocket("ws://localhost:8000/ws/interview");
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.onmessage = (event) => {
      // Audio From Backed
      if (event.data instanceof ArrayBuffer) {
        playAudio(event.data, audioCtx);
        return;
      }

      // Text / State from Backend
      if (typeof event.data === "string") {
        const msg = JSON.parse(event.data);
      
        if (msg.type === "avatar_sync") {
          setAvatarText(msg.text);
        }
      }
    };

    socketRef.current = ws;

    return () => {
      ws.close();
      audioCtx.close();
    };
  }, []);

  return {
    avatarText,
  };
}
/**
 * Plays raw PCM audio sent from backend
 * (This will later be replaced with real TTS audio)
 */
function playAudio(buffer: ArrayBuffer, audioCtx: AudioContext) {
  const floatData = new Float32Array(buffer);

  const audioBuffer = audioCtx.createBuffer(
    1,
    floatData.length,
    audioCtx.sampleRate
  );

  audioBuffer.copyToChannel(floatData, 0);

  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioCtx.destination);
  source.start();
}