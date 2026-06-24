import { useEffect, useRef, useCallback } from "react";

interface AudioStreamHandlerProps {
  isActive: boolean;
  onAudioChunk?: (audioChunk: Blob) => void;
  onSpeechEnd?: () => void;
  silenceThreshold?: number;
  silenceDuration?: number; // ms
}

export default function AudioStreamHandler({
  isActive,
  onAudioChunk,
  onSpeechEnd,
  silenceThreshold = 0.01,
  silenceDuration = 1500,
}: AudioStreamHandlerProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const silenceTimerRef = useRef<number | null>(null);
  const isListeningRef = useRef(false);

  const stopStream = useCallback(() => {
    if (silenceTimerRef.current) {
      window.clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    isListeningRef.current = false;
  }, []);

  const startStream = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // Set up audio analysis for VAD
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      source.connect(analyser);

      // Set up MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      // Data available handler
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0 && onAudioChunk) {
          console.log(`Audio chunk sent: ${event.data.size} bytes`);
          onAudioChunk(event.data);
        }
      };

      // Start recording with small chunks
      recorder.start(300);
      console.log("MediaRecorder started");
      isListeningRef.current = true;

      // Start audio level monitoring for VAD
      const checkAudioLevel = () => {
        if (!analyserRef.current || !isActive) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate average volume
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const avg = sum / dataArray.length;
        const normalizedLevel = avg / 255;

        // Check for silence
        if (normalizedLevel < silenceThreshold) {
          if (!silenceTimerRef.current) {
            // Start silence timer
            silenceTimerRef.current = window.setTimeout(() => {
              if (onSpeechEnd) {
                onSpeechEnd();
              }
            }, silenceDuration);
          }
        } else {
          // Reset silence timer when there's speech
          if (silenceTimerRef.current) {
            window.clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        }

        if (isActive && mediaRecorderRef.current?.state === "recording") {
          requestAnimationFrame(checkAudioLevel);
        }
      };

      requestAnimationFrame(checkAudioLevel);
    } catch (error) {
      console.error("Error starting audio stream:", error);
    }
  }, [isActive, onAudioChunk, onSpeechEnd, silenceThreshold, silenceDuration]);

  // Start/stop based on isActive prop
  useEffect(() => {
    if (isActive && !isListeningRef.current) {
      void startStream();
    } else if (!isActive && isListeningRef.current) {
      stopStream();
    }

    return () => {
      stopStream();
    };
  }, [isActive, startStream, stopStream]);

  // Expose audio level for UI visualization
  useEffect(() => {
    return () => {
      if (silenceTimerRef.current) {
        window.clearTimeout(silenceTimerRef.current);
      }
    };
  }, []);

  return null; // This component doesn't render anything
}

