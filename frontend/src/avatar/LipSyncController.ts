import type { VRM } from "@pixiv/three-vrm";
import { allMappedVisemes, visemeMap } from "./visemeMap";

export type VisemeCue = {
  start: number;
  end: number;
  viseme: number;
};

export function applyLipSync(
  vrm: VRM,
  elapsedTimeMs: number,
  visemes: VisemeCue[] | undefined
) {
  if (!visemes?.length || !vrm.expressionManager) return;

  const active = visemes.find((v) => elapsedTimeMs >= v.start && elapsedTimeMs <= v.end);

  for (const key of allMappedVisemes) {
    vrm.expressionManager.setValue(key, 0);
  }

  if (!active) return;

  const viseme = visemeMap[active.viseme];
  if (!viseme) return;

  vrm.expressionManager.setValue(viseme, 1);
}
