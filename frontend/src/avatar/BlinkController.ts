import type { VRM } from "@pixiv/three-vrm";

let blinkTimer = 0;

export function applyBlink(vrm: VRM, delta: number) {
  if (!vrm.expressionManager) return;

  blinkTimer += delta;
  const blink = Math.max(0, Math.sin(blinkTimer * 2.5));
  vrm.expressionManager.setValue("blink", blink);
}
