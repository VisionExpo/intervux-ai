import type { RefObject } from "react";
import AvatarScene from "../../avatar/AvatarScene";
import type { VisemeCue } from "../../avatar/LipSyncController";

type Props = {
  isSpeacking: boolean;
  audioRef: RefObject<HTMLAudioElement | null>;
  visemes?: VisemeCue[];
  avatarState?: "speaking" | "listening" | "thinking";
  emotion?: string;
};

export default function Avatar3D({
  isSpeacking,
  audioRef,
  visemes,
  avatarState = "listening",
  emotion = "neutral",
}: Props) {
  return (
    <div style={{ width: "100%", maxWidth: "720px" }}>
      <AvatarScene
        audioRef={audioRef}
        visemes={visemes}
        avatarState={avatarState}
        emotion={emotion}
      />
      <p style={{ marginTop: "0.4rem", fontSize: "0.85rem", color: "#666" }}>
        Avatar state: {avatarState} ({isSpeacking ? "audio on" : "audio off"})
      </p>
    </div>
  );
}
