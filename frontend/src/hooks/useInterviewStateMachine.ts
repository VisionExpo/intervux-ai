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
  | { type: "WS_CONNECTING" }
  | { type: "WS_CONNECTED" }
  | { type: "RESUME_UPLOAD_START" }
  | { type: "RESUME_PROCESS_SUCCESS" }
  | { type: "QUESTION_RECEIVED" }
  | { type: "PHASE_LISTENING" }
  | { type: "ANSWER_PROCESSING_START" }
  | { type: "EVALUATION_COMPLETE" }
  | { type: "INTERVIEW_COMPLETE" }
  | { type: "SET_PHASE"; phase: InterviewState }
  | { type: "ERROR_OCCURRED" }
  | { type: "RESET" };

export const initialState: InterviewState = "CONNECTING";

export function interviewReducer(
  state: InterviewState,
  action: InterviewAction
): InterviewState {
  console.log(`STATE: ${state} → ACTION: ${action.type}`);

  // Handle global actions first
  if (action.type === "RESET") {
    return "CONNECTING";
  }
  if (action.type === "ERROR_OCCURRED") {
    return "ERROR";
  }
  if (action.type === "SET_PHASE") {
    if (state === action.phase) return state;
    return action.phase;
  }

  switch (state) {
    case "CONNECTING":
      switch (action.type) {
        case "WS_CONNECTED":
          return "WAITING_RESUME";
        default:
          return state;
      }

    case "WAITING_RESUME":
      switch (action.type) {
        case "RESUME_UPLOAD_START":
          return "PROCESSING_RESUME";
        default:
          return state;
      }

    case "PROCESSING_RESUME":
    case "ASKING_QUESTION":
    case "LISTENING":
    case "PROCESSING_ANSWER":
    case "NEXT_QUESTION":
    case "INTERVIEW_COMPLETE":
    case "ERROR":
      return state;

    default:
      return state;
  }
}
