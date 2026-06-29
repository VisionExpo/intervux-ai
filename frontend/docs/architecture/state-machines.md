# State Machines

## Purpose
To provide deterministic, predictable flow control for both the overarching interview and the granular AI agent states.

## Implementations
1. **Interview State Machine**: Manages the macro phases of the session (Idle -> Resume Upload -> Greeting -> Behavioral -> Technical -> Finished).
2. **AI State Machine**: Manages the micro states of the AI agent within a single turn (Thinking -> Analyzing -> Generating -> Synthesizing -> Speaking).

The UI *must only* react to these formal states, avoiding arbitrary local boolean flags (e.g., no `isAiThinking` or `isProcessing`).
