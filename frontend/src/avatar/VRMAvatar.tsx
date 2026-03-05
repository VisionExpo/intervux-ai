import { useEffect, useRef, useState, type RefObject } from "react";
import { useFrame } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { VRM, VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import type { VisemeCue } from "./LipSyncController";
import { applyLipSync } from "./LipSyncController";
import { applyBlink } from "./BlinkController";

type VRMAvatarProps = {
  audioRef: RefObject<HTMLAudioElement | null>;
  visemes?: VisemeCue[];
};

export default function VRMAvatar({ audioRef, visemes }: VRMAvatarProps) {
  const vrmRef = useRef<VRM | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const loader = new GLTFLoader();
    let cancelled = false;
    loader.register((parser) => new VRMLoaderPlugin(parser));

    loader.load(
      "/avatar.vrm",
      (gltf) => {
        VRMUtils.removeUnnecessaryJoints(gltf.scene);
        const vrm = gltf.userData.vrm as VRM | undefined;
        if (!vrm || cancelled) return;

        vrm.scene.rotation.y = Math.PI;
        vrmRef.current = vrm;
        setLoaded(true);
      },
      undefined,
      () => {
        if (!cancelled) {
          setLoaded(false);
        }
      }
    );

    return () => {
      cancelled = true;
    };
  }, []);

  useFrame((_state, delta) => {
    const vrm = vrmRef.current;
    if (!vrm) return;

    applyBlink(vrm, delta);
    applyLipSync(vrm, audioRef.current, visemes);
    vrm.update(delta);
  });

  if (!loaded || !vrmRef.current) return null;

  return <primitive object={vrmRef.current.scene} scale={1.4} />;
}
