import { useEffect, useRef, useState } from "react";

interface CandidateCameraProps {
  isEnabled?: boolean;
  stream?: MediaStream | null;
}

export default function CandidateCamera({ isEnabled = true, stream }: CandidateCameraProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [hasCamera, setHasCamera] = useState(false);
  const [cameraError, setCameraError] = useState<string>("");
  const [micActive, setMicActive] = useState(false);

  useEffect(() => {
    if (!isEnabled || !stream) {
      setHasCamera(false);
      return;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      setHasCamera(true);
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

