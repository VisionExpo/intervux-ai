import { useEffect, useRef, useState, type RefObject } from "react";
import { useFrame } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRM, VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import type { Object3D } from "three";
import type { VisemeCue } from "./LipSyncController";
import { applyLipSync } from "./LipSyncController";
import { applyBlink } from "./BlinkController";

type VRMAvatarProps = {
  audioRef: RefObject<HTMLAudioElement | null>;
  visemes?: VisemeCue[];
  avatarState: "speaking" | "listening" | "thinking";
  emotion: string;
  onLoadError?: () => void;
};

export default function VRMAvatar({
  audioRef,
  visemes,
  avatarState,
  emotion,
  onLoadError,
}: VRMAvatarProps) {
  const vrmRef = useRef<VRM | null>(null);
  const headRef = useRef<Object3D | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const loader = new GLTFLoader();
    let cancelled = false;
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      "/avatar.vrm",
      (gltf) => {
        try {
          VRMUtils.removeUnnecessaryJoints(gltf.scene);
          const vrm = gltf.userData.vrm as VRM | undefined;
          if (!vrm || cancelled) {
            if (!cancelled && !vrm) {
              setLoaded(false);
              onLoadError?.();
            }
            return;
          }

          vrm.scene.rotation.y = Math.PI;
          vrmRef.current = vrm;
          headRef.current =
            (vrm.humanoid as { getNormalizedBoneNode?: (name: string) => Object3D | null })
              ?.getNormalizedBoneNode?.("head") ?? null;
          setLoaded(true);
        } catch {
          if (!cancelled) {
            setLoaded(false);
            onLoadError?.();
          }
        }
      },
      undefined,
      () => {
        if (!cancelled) {
          setLoaded(false);
          onLoadError?.();
        }
      }
    );

    return () => {
      cancelled = true;
    };
  }, []);

  useFrame((state, delta) => {
    const vrm = vrmRef.current;
    if (!vrm) return;

    applyBlink(vrm, delta);
    applyLipSync(vrm, audioRef.current, visemes);
    applyAvatarBehavior(vrm, headRef.current, avatarState, emotion, state.clock.elapsedTime, state.camera.position);
    vrm.update(delta);
  });

  if (!loaded || !vrmRef.current) return null;

  return <primitive object={vrmRef.current.scene} scale={1.4} />;
}

function applyAvatarBehavior(
  vrm: VRM,
  head: Object3D | null,
  avatarState: "speaking" | "listening" | "thinking",
  emotion: string,
  elapsedTime: number,
  cameraPosition: { x: number; y: number; z: number }
) {
  if (head) {
    head.lookAt(cameraPosition.x, cameraPosition.y + 0.02, cameraPosition.z);

    if (avatarState === "listening") {
      head.rotation.x += Math.sin(elapsedTime * 2.8) * 0.02;
    } else if (avatarState === "thinking") {
      head.rotation.x += 0.08;
      head.rotation.y += Math.sin(elapsedTime * 0.9) * 0.04;
    } else {
      head.rotation.y += Math.sin(elapsedTime * 1.8) * 0.02;
    }
  }

  if (!vrm.expressionManager) return;

  vrm.expressionManager.setValue("happy", 0);
  vrm.expressionManager.setValue("relaxed", 0);
  vrm.expressionManager.setValue("sad", 0);

  const normalized = emotion.toLowerCase();
  if (normalized === "supportive" || normalized === "encouraging") {
    vrm.expressionManager.setValue("happy", 0.35);
  } else if (normalized === "thinking" || avatarState === "thinking") {
    vrm.expressionManager.setValue("relaxed", 0.2);
  } else if (normalized === "stressed") {
    vrm.expressionManager.setValue("sad", 0.18);
  }
}
