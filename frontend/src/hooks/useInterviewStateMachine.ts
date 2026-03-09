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
      switch (action.type) {
        case "RESUME_PROCESS_SUCCESS":
          return "ASKING_QUESTION"; // Go directly to asking question
        default:
          return state;
      }
    
    case "ASKING_QUESTION":
      switch (action.type) {
        case "PHASE_LISTENING":
          return "LISTENING";
        default:
          return state;
      }

    case "LISTENING":
      switch (action.type) {
        case "ANSWER_PROCESSING_START":
          return "PROCESSING_ANSWER";
        default:
          return state;
      }

    case "PROCESSING_ANSWER":
      switch (action.type) {
        case "EVALUATION_COMPLETE":
          return "NEXT_QUESTION";
        case "INTERVIEW_COMPLETE":
          return "INTERVIEW_COMPLETE";
        default:
          return state;
      }

    case "NEXT_QUESTION":
      switch (action.type) {
        case "QUESTION_RECEIVED":
          return "ASKING_QUESTION";
        default:
          return state;
      }
    
    case "INTERVIEW_COMPLETE":
      // Terminal state, only RESET can change it
      return state;

    case "ERROR":
      // Terminal state, only RESET can change it
      return state;

    default:
      return state;
  }
}
