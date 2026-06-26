import { Suspense, useEffect, useRef, useState } from "react";
import { useInterviewSession } from "../providers/InterviewSessionProvider";
import { audioFeedback } from "../utils/audioFeedback";
import {
  InterviewLayout,
  AvatarInterviewer,
  CodingSandbox,
  CandidateCamera,
  TranscriptPanel,
} from "../components/interview";
import { Button } from "../components/ui/Button/Button";
import { CheckCircle2, ChevronRight, Play, LayoutDashboard } from "lucide-react";
import styles from "./InterviewOverlay.module.css";
import { authFetch } from "../hooks/authFetch";
import { useNavigate } from "react-router-dom";
import { ErrorBoundary } from "../components/ErrorBoundary";

const DEMO_LIGHT_MODE = import.meta.env.VITE_DEMO_LIGHT_MODE === "true";

export default function InterviewPage() {
  const {
    stage,
    avatarState,
    avatarText,
    isSpeaking,
    isConnected,
    questionIndex,
    totalQuestions,
    lastEvaluation,
    finalReport,
    audioContextRef,
    playbackStartTimeRef,
    visemesRef,
    emotion,
    transcriptMessages,
    mediaStream,
    startAudioStream,
    stopAudioStream,
    endAnswer,
    lastError,
    uploadResume,
  } = useInterviewSession();

  const prevStageRef = useRef(stage);
  const latestStageRef = useRef(stage);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // DB-4: Initialize or resume AudioContext on user interaction to prevent iOS/Chrome autoplay blocks
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext();
    } else if (audioContextRef.current.state === "suspended") {
      audioContextRef.current.resume().catch((err) => console.warn("Failed to resume AudioContext", err));
    }

    const file = e.target.files?.[0];
    if (file) {
      await uploadResume(file);
    }
  };

  const connectionStatus = isConnected
    ? "connected"
    : stage === "CONNECTING"
    ? "connecting"
    : "disconnected";

  const isListening = stage === "LISTENING";
  const currentQuestion = lastEvaluation?.question || avatarText;

  useEffect(() => {
    if (stage === "LISTENING") {
      startAudioStream();
    } else {
      stopAudioStream();
    }
  }, [stage, startAudioStream, stopAudioStream]);

  useEffect(() => {
    latestStageRef.current = stage;

    if (prevStageRef.current !== stage) {
      console.log(`Stage transition: ${prevStageRef.current} -> ${stage}`);
      switch (stage) {
        case "LISTENING":
          audioFeedback.listeningStart();
          break;
        case "PROCESSING_ANSWER":
          audioFeedback.processing();
          break;
        case "ASKING_QUESTION":
        case "NEXT_QUESTION":
          audioFeedback.questionEnd();
          break;
        case "INTERVIEW_COMPLETE":
          audioFeedback.interviewComplete();
          break;
      }
      prevStageRef.current = stage;
    }
  }, [stage]);

  useEffect(() => {
    console.log("[InterviewPage] mounted");
    return () => {
      console.warn("[InterviewPage] unmounted", { stage: latestStageRef.current });
      audioFeedback.dispose();
    };
  }, []);

  useEffect(() => {
    if (stage === "INTERVIEW_COMPLETE") {
      // Logic for storing report is already handled in useInterview or useEffect above
    }
  }, [stage]);

  const [overlayVisible, setOverlayVisible] = useState(false);

  useEffect(() => {
    if (stage === "INTERVIEW_COMPLETE" && !overlayVisible) {
      setOverlayVisible(true);
    }
  }, [stage, overlayVisible]);

  if (overlayVisible || stage === "INTERVIEW_COMPLETE") {
    return <InterviewOverlay finalReport={finalReport} />;
  }

  if (stage === "CONNECTING") {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-slate-900 to-slate-700 text-white">
        <div className="text-4xl mb-4 animate-bounce">🎙️</div>
        <h2 className="text-2xl font-bold mb-2">Connecting to Interview...</h2>
        <p className="text-slate-400">Please wait while we establish a connection</p>
        {lastError && (
          <p className="text-red-500 mt-4 px-4 py-2 bg-red-500/10 rounded-md border border-red-500/20">{lastError}</p>
        )}
      </div>
    );
  }

  const showResumeUpload = stage === "WAITING_RESUME" || stage === "PROCESSING_RESUME";

  const getResumeUploadText = () => {
    if (stage === "PROCESSING_RESUME") {
      return "Analyzing your experience...";
    }
    return "Please upload your resume to start the interview. The AI will use it to personalize questions.";
  };
  
  return (
    <InterviewLayout
      connectionStatus={connectionStatus}
      questionNumber={questionIndex}
      totalQuestions={totalQuestions}
      avatarPanel={
        showResumeUpload ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-slate-50/50 backdrop-blur-sm rounded-xl">
            <div className="text-5xl mb-4">
              {stage === "PROCESSING_RESUME" ? (
                <span className="inline-block animate-spin">⏳</span>
              ) : (
                "📄"
              )}
            </div>
            <h2 className="text-slate-800 text-2xl font-bold mb-4">
              {stage === "PROCESSING_RESUME" ? "Processing Resume" : "Upload Your Resume"}
            </h2>
            <p className="text-slate-600 mb-6 max-w-md mx-auto">
              {getResumeUploadText()}
            </p>
            {stage === "WAITING_RESUME" && (
              <div className="mb-4">
                <label className="cursor-pointer bg-white border border-slate-300 hover:border-blue-400 hover:bg-blue-50 transition-colors rounded-lg px-6 py-3 flex items-center justify-center shadow-sm">
                  <span className="text-blue-600 font-medium">Select Resume File (.pdf, .doc)</span>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </label>
              </div>
            )}
          </div>
        ) : (
          <ErrorBoundary fallback={<SpeakerOrb isSpeaking={isSpeaking} avatarState={avatarState} questionText={currentQuestion} />}>
            <Suspense fallback={<SpeakerOrb isSpeaking={isSpeaking} avatarState={avatarState} questionText={currentQuestion} />}>
              {DEMO_LIGHT_MODE ? (
                <SpeakerOrb isSpeaking={isSpeaking} avatarState={avatarState} questionText={currentQuestion} />
              ) : (
                <AvatarInterviewer
                  isSpeaking={isSpeaking}
                  audioContextRef={audioContextRef}
                  playbackStartTimeRef={playbackStartTimeRef}
                  visemesRef={visemesRef}
                  avatarState={avatarState}
                  emotion={emotion}
                  questionText={currentQuestion}
                />
              )}
            </Suspense>
          </ErrorBoundary>
        )
      }
      codingPanel={
        <CodingSandbox
          language="python"
          problemDescription={
            lastEvaluation?.question?.includes("code")
              ? lastEvaluation.question
              : "Implement a function that finds two numbers that add up to a target."
          }
        />
      }
      transcriptPanel={
        <TranscriptPanel
          messages={transcriptMessages}
          isListening={isListening}
          onEndAnswer={endAnswer}
        />
      }
      cameraPanel={
        <CandidateCamera 
          isEnabled={true} 
          stream={mediaStream} 
          isListening={isListening} 
          isSpeaking={isSpeaking} 
        />
      }
    />
  );
}

function SpeakerOrb({
  isSpeaking,
  avatarState,
  questionText,
}: {
  isSpeaking: boolean;
  avatarState: "speaking" | "listening" | "thinking";
  questionText?: string;
}) {
  useEffect(() => {
    console.log("[SpeakerOrb] mounted");
    return () => console.warn("[SpeakerOrb] unmounted");
  }, []);

  const label = isSpeaking
    ? "Speaking"
    : avatarState === "listening"
    ? "Listening"
    : "Thinking";

  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-6 bg-slate-50/70 p-8 text-center">
      <div
        className={`h-32 w-32 rounded-full bg-gradient-to-br from-cyan-400 via-blue-500 to-emerald-400 shadow-2xl ${
          isSpeaking ? "animate-pulse" : ""
        }`}
        aria-hidden="true"
      />
      <div>
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">{label}</p>
        <p className="mx-auto max-w-xl text-base leading-7 text-slate-700">
          {questionText || "Preparing the next interview prompt..."}
        </p>
      </div>
    </div>
  );
}

function InterviewOverlay({ finalReport }: { finalReport: any }) {
  const navigate = useNavigate();
  const [timeLeft, setTimeLeft] = useState(10);
  const [isPaused, setIsPaused] = useState(false);
  const [isStartingAnother, setIsStartingAnother] = useState(false);

  useEffect(() => {
    if (isPaused || timeLeft <= 0) return;

    const timer = setTimeout(() => {
      setTimeLeft(timeLeft - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [timeLeft, isPaused]);

  useEffect(() => {
    if (timeLeft === 0 && !isPaused) {
      navigate("/interviews");
    }
  }, [timeLeft, isPaused, navigate]);

  const handleStartAnother = async () => {
    setIsStartingAnother(true);
    setIsPaused(true); // Stop the countdown
    try {
      const response = await authFetch<{
        session_id: string;
      }>("/api/candidate/mock-interview/start", { method: "POST" });

      sessionStorage.setItem("mock_session_id", response.session_id);
      // Fresh navigation to re-initialize useInterview hook
      window.location.href = `#/interview-session?mock_session_id=${encodeURIComponent(response.session_id)}`;
      window.location.reload(); // Force full re-init for fresh socket & state
    } catch (err) {
      console.error("Failed to start another interview:", err);
      navigate("/interviews");
    }
  };

  const score = (finalReport?.overall_score || finalReport?.score || 0).toFixed(0);

  return (
    <div className={styles.overlayBackdrop}>
      <div 
        className={styles.overlayCard}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => timeLeft > 0 && setIsPaused(false)}
      >
        <div className={styles.iconWrap}>
          <CheckCircle2 size={40} />
        </div>
        
        <h2 className={styles.title}>Interview Complete!</h2>
        <p className={styles.subtitle}>Our AI has finished gathering evaluation data.</p>

        <div className={styles.scoreContainer}>
          <p className={styles.scoreLabel}>Overall Score</p>
          <div className={styles.scoreValue}>{score}<span>%</span></div>
        </div>

        <div className={styles.actions}>
          <Button 
            onClick={() => navigate(`/report/${sessionStorage.getItem("mock_session_id")}`)}
            fullWidth
          >
            View Full Report <ChevronRight size={18} />
          </Button>
          
          <Button 
            variant="secondary" 
            onClick={handleStartAnother}
            disabled={isStartingAnother}
            fullWidth
          >
            {isStartingAnother ? "Preparing..." : <><Play size={16} /> Start Another</>}
          </Button>

          <Button 
            variant="secondary" 
            onClick={() => navigate("/interviews")}
            fullWidth
          >
            <LayoutDashboard size={16} /> Back to Hub
          </Button>
        </div>

        {!isPaused && timeLeft > 0 && (
          <div 
            className={styles.timerBar} 
            style={{ 
              transform: `scaleX(${timeLeft / 10})`,
              transition: 'transform 1s linear'
            }} 
          />
        )}
        
        <p className={styles.timerText}>
          {isPaused ? "Timer paused" : `Redirecting to hub in ${timeLeft}s...`}
        </p>
      </div>
    </div>
  );
}
