import type { RefObject } from "react";
import AvatarScene from "../../avatar/AvatarScene";
import type { VisemeCue } from "../../avatar/LipSyncController";

type Props = {
  isSpeaking: boolean;
  audioContextRef: RefObject<AudioContext | null>;
  playbackStartTimeRef: RefObject<number>;
  visemesRef: RefObject<VisemeCue[]>;
  avatarState?: "speaking" | "listening" | "thinking";
  emotion?: string;
};

export default function Avatar3D({
  isSpeaking,
  audioContextRef,
  playbackStartTimeRef,
  visemesRef,
  avatarState = "listening",
  emotion = "neutral",
}: Props) {
  return (
    <div style={{ width: "100%", maxWidth: "720px" }}>
      <AvatarScene
        audioContextRef={audioContextRef}
        playbackStartTimeRef={playbackStartTimeRef}
        visemesRef={visemesRef}
        avatarState={avatarState}
        emotion={emotion}
      />
      <p style={{ marginTop: "0.4rem", fontSize: "0.85rem", color: "#666" }}>
        Avatar state: {avatarState} ({isSpeaking ? "audio on" : "audio off"})
      </p>
    </div>
  );
}
