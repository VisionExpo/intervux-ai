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
        emotion,
        avatarText
    } = useInterviewSession();

    return (
        <InterviewerView>
            <ErrorBoundary fallback={<FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} avatarText={avatarText} />}>
                <Suspense fallback={<FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} avatarText={avatarText} />}>
                    {DEMO_LIGHT_MODE ? (
                        <FallbackOrb isSpeaking={isSpeaking} avatarState={avatarState} avatarText={avatarText} />
                    ) : (
                        <AvatarInterviewer
                            isSpeaking={isSpeaking}
                            audioContextRef={audioContextRef}
                            playbackStartTimeRef={playbackStartTimeRef}
                            visemesRef={visemesRef}
                            avatarState={avatarState}
                            emotion={emotion}
                            questionText={avatarText}
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
  avatarText
}: {
  isSpeaking: boolean;
  avatarState: "speaking" | "listening" | "thinking";
  avatarText?: string;
}) {
  useEffect(() => {
    console.log("[FallbackOrb] mounted");
    return () => console.warn("[FallbackOrb] unmounted");
  }, []);

  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-12 p-8 text-center relative overflow-hidden bg-slate-950">
      {/* Background ambient glow */}
      <div 
        className={`absolute inset-0 bg-blue-900/10 blur-3xl transition-opacity duration-1000 ${isSpeaking ? 'opacity-100' : 'opacity-40'}`} 
      />
      
      {/* Dynamic Orb */}
      <div className="relative">
        {isSpeaking && (
          <div className="absolute -inset-4 rounded-full bg-cyan-400/20 blur-xl animate-pulse" />
        )}
        <div
          className={`h-40 w-40 rounded-full transition-all duration-700 shadow-2xl relative z-10 
            ${isSpeaking 
              ? "bg-gradient-to-br from-cyan-300 via-blue-500 to-indigo-600 scale-105 shadow-cyan-500/50" 
              : "bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 scale-100 shadow-slate-900/50"
            }`}
          style={{
             boxShadow: isSpeaking ? "0 0 40px rgba(6, 182, 212, 0.5)" : "inset 0 0 20px rgba(0,0,0,0.5)"
          }}
          aria-hidden="true"
        />
      </div>

      {/* Greeting / Subtitle Overlay */}
      <div 
        className={`relative z-10 max-w-lg transition-all duration-700 ${avatarText ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
      >
        <p className="text-xl font-medium text-slate-200 tracking-wide leading-relaxed">
          {avatarText}
        </p>
      </div>
    </div>
  );
}
