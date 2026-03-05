import type { VRM } from "@pixiv/three-vrm";
import { allMappedVisemes, visemeMap } from "./visemeMap";

export type VisemeCue = {
  start: number;
  end: number;
  viseme: number;
};

export function applyLipSync(
  vrm: VRM,
  audio: HTMLAudioElement | null,
  visemes: VisemeCue[] | undefined
) {
  if (!audio || !visemes?.length || !vrm.expressionManager) return;

  const time = audio.currentTime * 1000;
  const active = visemes.find((v) => time >= v.start && time <= v.end);

  for (const key of allMappedVisemes) {
    vrm.expressionManager.setValue(key, 0);
  }

  if (!active) return;

  const viseme = visemeMap[active.viseme];
  if (!viseme) return;

  vrm.expressionManager.setValue(viseme, 1);
}
