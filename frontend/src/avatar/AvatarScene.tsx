import { Canvas } from "@react-three/fiber";
import { Suspense, type RefObject } from "react";
import VRMAvatar from "./VRMAvatar";
import type { VisemeCue } from "./LipSyncController";

type AvatarSceneProps = {
  audioRef: RefObject<HTMLAudioElement | null>;
  visemes?: VisemeCue[];
};

export default function AvatarScene({ audioRef, visemes }: AvatarSceneProps) {
  return (
    <Canvas
      camera={{ position: [0, 1.4, 1.8], fov: 30 }}
      style={{ width: "100%", height: "420px" }}
    >
      <ambientLight intensity={0.8} />
      <directionalLight position={[0, 5, 5]} intensity={1} />

      <Suspense fallback={null}>
        <VRMAvatar audioRef={audioRef} visemes={visemes} />
      </Suspense>
    </Canvas>
  );
}
