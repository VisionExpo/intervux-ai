/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useRef, useState } from "react";

interface CandidateCameraProps {
  isEnabled?: boolean;
  stream?: MediaStream | null;
  isListening?: boolean;
  isSpeaking?: boolean;
}

export default function CandidateCamera({ isEnabled = true, stream, isListening, isSpeaking }: CandidateCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hasCamera = Boolean(isEnabled && stream);
  const [cameraError, setCameraError] = useState<string>("");
  const [micActive, setMicActive] = useState(false);

  useEffect(() => {
    if (!isEnabled || !stream) {

      return;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = stream;

      setCameraError("");

      const audioTrack = stream.getAudioTracks()[0];
      if (audioTrack) {
        setMicActive(audioTrack.enabled);
      } else {
        setMicActive(false);
      }
    }
  }, [isEnabled, stream]);

  return (
    <div className="w-full h-full relative">
      {hasCamera ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-preview absolute inset-0 w-full h-full object-cover transform -scale-x-100"
          />
          {/* Status Overlay */}
          <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black/60 to-transparent flex flex-col gap-2 z-10 text-white text-sm">
            
            {/* AI Status Indicator */}
            {(isListening || isSpeaking) && (
              <div className="flex items-center gap-2 mb-1">
                <span className="relative flex h-3 w-3">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isListening ? 'bg-green-400' : 'bg-blue-400'}`}></span>
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${isListening ? 'bg-green-500' : 'bg-blue-500'}`}></span>
                </span>
                <span className="font-semibold text-shadow-sm">
                  {isListening ? "AI is Listening..." : "AI is Speaking..."}
                </span>
              </div>
            )}
          {/* Camera Status */}
          <div className="flex justify-between items-center bg-black/40 backdrop-blur-sm rounded-full px-4 py-2 border border-white/10 shadow-sm font-medium">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${micActive ? "bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.6)]" : "bg-red-500"}`}></span>
              <span>{micActive ? "Mic Active" : "Mic Muted"}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.6)]"></span>
              <span>Camera On</span>
            </div>
          </div>
          </div>
        </>
      ) : (
        <div className="absolute inset-0 bg-slate-900 flex items-center justify-center text-white">
          <div className="text-center">
            {cameraError ? (
              <>
                <div className="text-3xl mb-2">📷</div>
                <div className="text-red-400">{cameraError}</div>
              </>
            ) : (
              <>
                <div className="text-3xl mb-2">⏳</div>
                <div className="text-slate-300">Initializing camera...</div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

