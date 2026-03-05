import { useRef } from "react";
import AvatarScene from "../../avatar/AvatarScene";
import type { VisemeCue } from "../../avatar/LipSyncController";

type Props = {
  isSpeacking: boolean;
  visemes?: VisemeCue[];
};

export default function Avatar3D({ isSpeacking, visemes }: Props) {
  const audioRef = useRef<HTMLAudioElement | null>(new Audio());

  return (
    <div style={{ width: "100%", maxWidth: "720px" }}>
      <AvatarScene audioRef={audioRef} visemes={visemes} />
      <p style={{ marginTop: "0.4rem", fontSize: "0.85rem", color: "#666" }}>
        Avatar state: {isSpeacking ? "speaking" : "idle"}
      </p>
    </div>
  );
}
