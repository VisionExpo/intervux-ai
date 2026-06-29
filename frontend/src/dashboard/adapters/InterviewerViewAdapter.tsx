import { Suspense, useEffect } from 'react';
import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { AvatarInterviewer } from '../../components/interview';
import { InterviewerView } from '../widgets/InterviewerView';
import { ErrorBoundary } from '../../components/ErrorBoundary';

const DEMO_LIGHT_MODE = import.meta.env.VITE_DEMO_LIGHT_MODE === "true";

export const InterviewerViewAdapter = () => {
    const {
        isSpeaking,
        audioContextRef,
        playbackStartTimeRef,
        visemesRef,
        avatarState,
        emotion
    } = useInterviewSession();

    return (
        <InterviewerView>
            <ErrorBoundary fallback={<FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} />}>
                <Suspense fallback={<FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} />}>
                    {DEMO_LIGHT_MODE ? (
                        <FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} />
                    ) : (
                        <AvatarInterviewer
                            isSpeaking={isSpeaking}
                            audioContextRef={audioContextRef}
                            playbackStartTimeRef={playbackStartTimeRef}
                            visemesRef={visemesRef}
                            avatarState={avatarState}
                            emotion={emotion}
                            questionText=""
                        />
                    )}
                </Suspense>
            </ErrorBoundary>
        </InterviewerView>
    );
};

function FallbackOrb({
  isSpeaking,
  avatarState,
}: {
  isSpeaking: boolean;
  avatarState: "speaking" | "listening" | "thinking";
}) {
  useEffect(() => {
    console.log("[FallbackOrb] mounted");
    return () => console.warn("[FallbackOrb] unmounted");
  }, []);

  // avatarState can be used later to customize the fallback
  console.log("Avatar state:", avatarState);

  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-6 p-8 text-center">
      <div
        className={`h-32 w-32 rounded-full bg-gradient-to-br from-cyan-400 via-blue-500 to-emerald-400 shadow-2xl ${
          isSpeaking ? "animate-pulse" : ""
        }`}
        aria-hidden="true"
      />
    </div>
  );
}
