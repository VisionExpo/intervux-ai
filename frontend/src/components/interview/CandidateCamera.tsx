import { useEffect, useRef, useState } from "react";

interface CandidateCameraProps {
  isEnabled?: boolean;
}

export default function CandidateCamera({ isEnabled = true }: CandidateCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [hasCamera, setHasCamera] = useState(false);
  const [cameraError, setCameraError] = useState<string>("");
  const [micActive, setMicActive] = useState(false);

  useEffect(() => {
    if (!isEnabled) return;

    async function initCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setHasCamera(true);
          setCameraError("");

          // Check if audio track is active
          const audioTrack = stream.getAudioTracks()[0];
          if (audioTrack) {
            setMicActive(audioTrack.enabled);
          }
        }
      } catch (err) {
        console.error("Camera access error:", err);
        setCameraError("Camera access denied or not available");
        setHasCamera(false);
      }
    }

    initCamera();

    return () => {
      // Cleanup: stop all tracks
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [isEnabled]);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      {hasCamera ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-preview"
            style={{
              transform: "scaleX(-1)", // Mirror the video
            }}
          />
          {/* Camera Status */}
          <div className="camera-status">
            <div className="status-item">
              <span className={`status-dot ${micActive ? "active" : "inactive"}`}></span>
              <span>Mic: {micActive ? "Active" : "Muted"}</span>
            </div>
            <div className="status-item">
              <span className="status-dot active"></span>
              <span>Camera: On</span>
            </div>
          </div>
        </>
      ) : (
        <div className="camera-overlay">
          <div style={{ textAlign: "center" }}>
            {cameraError ? (
              <>
                <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📷</div>
                <div>{cameraError}</div>
              </>
            ) : (
              <>
                <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⏳</div>
                <div>Initializing camera...</div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

