import { useEffect, useRef, useState } from "react";

export function useAvatarSocket() {
  const socketRef = useRef<WebSocket | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  const [avatarText, setAvatarText] = useState<string>("");

  useEffect(() => {
    // 1️⃣ Create WebSocket
    const ws = new WebSocket("ws://localhost:8000/ws/interview");
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      console.log("✅ WebSocket connected");
    };

    ws.onmessage = (event) => {
      if (typeof event.data === "string") {
        const msg = JSON.parse(event.data);

        if (msg.type === "avatar_sync") {
          setAvatarText(msg.text);
        }
      }
    };

    socketRef.current = ws;

    // 2️⃣ Setup microphone capture
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const audioCtx = new AudioContext({ sampleRate: 16000 });
      audioCtxRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      const processor = audioCtx.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(audioCtx.destination);

      processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);

        // Convert Float32 → ArrayBuffer
        const buffer = new Float32Array(input).buffer;

        socketRef.current?.send(buffer);
      };
    });

    return () => {
      ws.close();
      audioCtxRef.current?.close();
    };
  }, []);

  return {
    avatarText,
  };
}
