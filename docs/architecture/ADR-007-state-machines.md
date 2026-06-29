# ADR 007: Formal State Machines

## Context
Interview progression (Waiting for Resume -> Processing -> Connecting -> Asking -> Listening -> Evaluating) is highly sequential but prone to race conditions (e.g., user speaks before TTS finishes).

## Decision
We enforce strict transitions using explicit State Machines for critical flows (Session State, Audio State, Connection State).

## Alternatives
- Booleans (isListening, isConnecting, isSpeaking) (rejected: leads to impossible states like isListening=true && isSpeaking=true).

## Tradeoffs
- Overhead in defining states and valid transitions.

## Consequences
- Predictable behavior. We can guarantee that the microphone is never active while the Avatar is speaking, preventing feedback loops.

## Future evolution
State Machines make it trivial to emit telemetry on how long candidates spend in specific stages, enabling deep workflow analytics.