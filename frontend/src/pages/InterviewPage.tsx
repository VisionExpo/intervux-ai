import { useEffect, useRef } from "react";
import { useInterview } from "../hooks/useInterview";
import { audioFeedback } from "../utils/audioFeedback";
import {
  InterviewLayout,
  AvatarInterviewer,
  CodingSandbox,
  CandidateCamera,
  TranscriptPanel,
} from "../components/interview";

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
    audioRef,
    visemes,
    emotion,
    transcriptMessages,
    mediaStream,
    startAudioStream,
    stopAudioStream,
    lastError,
    uploadResume,
  } = useInterview();

  const prevStageRef = useRef(stage);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
    return () => {
      audioFeedback.dispose();
    };
  }, []);

  useEffect(() => {
    if (stage === "INTERVIEW_COMPLETE" && finalReport) {
      sessionStorage.setItem("interview_report", JSON.stringify(finalReport));
      window.location.hash = "#/report";
    }
  }, [stage, finalReport]);

  if (stage === "INTERVIEW_COMPLETE" && finalReport) {
    return null;
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
          <AvatarInterviewer
            isSpeaking={isSpeaking}
            audioRef={audioRef}
            visemes={visemes}
            avatarState={avatarState}
            emotion={emotion}
            questionText={currentQuestion}
          />
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
