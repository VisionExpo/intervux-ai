import { createContext, useContext, useEffect, useRef, type ReactNode } from "react";
import { useInterview } from "../hooks/useInterview";

import { RuntimeProvider } from "./RuntimeProvider";

type InterviewSessionValue = ReturnType<typeof useInterview>;

const InterviewSessionContext = createContext<InterviewSessionValue | null>(null);

export function InterviewSessionProvider({ children }: { children: ReactNode }) {
  return (
    <RuntimeProvider>
       <InterviewSessionInnerProvider>
          {children}
       </InterviewSessionInnerProvider>
    </RuntimeProvider>
  );
}

function InterviewSessionInnerProvider({ children }: { children: ReactNode }) {
  const session = useInterview();
  const latestSessionRef = useRef(session);

  useEffect(() => {
    latestSessionRef.current = session;
  }, [session]);

  useEffect(() => {
    console.log("[InterviewSessionProvider] mounted");
    return () => {
      const latestSession = latestSessionRef.current;
      console.warn("[InterviewSessionProvider] unmounted", {
        phase: latestSession.stage,
        connected: latestSession.isConnected,
      });
    };
  }, []);

  return (
    <InterviewSessionContext.Provider value={session}>
      {children}
    </InterviewSessionContext.Provider>
  );
}

export function useInterviewSession() {
  const session = useContext(InterviewSessionContext);
  if (!session) {
    throw new Error("useInterviewSession must be used within InterviewSessionProvider");
  }
  return session;
}
