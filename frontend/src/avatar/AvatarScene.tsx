import { Canvas } from "@react-three/fiber";
import { Suspense, useState, type RefObject } from "react";
import VRMAvatar from "./VRMAvatar";
import type { VisemeCue } from "./LipSyncController";

type AvatarSceneProps = {
  audioContextRef: RefObject<AudioContext | null>;
  playbackStartTimeRef: RefObject<number>;
  visemesRef: RefObject<VisemeCue[]>;
  avatarState?: "speaking" | "listening" | "thinking";
  emotion?: string;
};

// Fallback avatar when VRM file is unavailable
const AvatarFallback = () => (
  <div
    style={{
      width: 120,
      height: 120,
      borderRadius: "50%",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: 48,
      color: "white",
      fontWeight: "bold",
      margin: "0 auto",
    }}
  >
    AI
  </div>
);

export default function AvatarScene({
  audioContextRef,
  playbackStartTimeRef,
  visemesRef,
  avatarState = "listening",
  emotion = "neutral",
}: AvatarSceneProps) {
  const [avatarLoadFailed, setAvatarLoadFailed] = useState(false);

  if (avatarLoadFailed) {
    return <AvatarFallback />;
  }

  return (
    <Canvas
      camera={{ position: [0, 1.45, 1.2], fov: 35 }}
      style={{ width: "100%", height: "500px" }}
    >
      <ambientLight intensity={0.8} />
      <directionalLight position={[0, 5, 5]} intensity={1} />

      <Suspense fallback={null}>
        <VRMAvatar
          audioContextRef={audioContextRef}
          playbackStartTimeRef={playbackStartTimeRef}
          visemesRef={visemesRef}
          avatarState={avatarState}
          emotion={emotion}
          onLoadError={() => setAvatarLoadFailed(true)}
        />
      </Suspense>
    </Canvas>
  );
}
