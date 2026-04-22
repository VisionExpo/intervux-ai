export type InterviewState =
  | "CONNECTING"
  | "WAITING_RESUME"
  | "PROCESSING_RESUME"
  | "ASKING_QUESTION"
  | "LISTENING"
  | "PROCESSING_ANSWER"
  | "NEXT_QUESTION"
  | "INTERVIEW_COMPLETE"
  | "ERROR";

export type InterviewAction =
  | { type: "SET_PHASE"; phase: InterviewState }
  | { type: "ERROR_OCCURRED" }
  | { type: "RESET" }
  | { type: "WS_CONNECTING" }
  | { type: "WS_CONNECTED" };

export const initialState: InterviewState = "CONNECTING";

export function interviewReducer(
  state: InterviewState,
  action: InterviewAction
): InterviewState {
  console.log(`[STATE] ${state} → [ACTION] ${action.type}`, action);

  switch (action.type) {
    case "SET_PHASE":
      if (state === action.phase) return state;
      return action.phase;
    
    case "RESET":
      return "CONNECTING";
      
    case "ERROR_OCCURRED":
      return "ERROR";
      
    case "WS_CONNECTING":
      return "CONNECTING";
      
    case "WS_CONNECTED":
      // We stay in CONNECTING until the backend sends the first PHASE_CHANGE
      return state;
      
    default:
      return state;
  }
}
