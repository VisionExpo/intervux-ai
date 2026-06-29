# ADR 001: Runtime Extraction

## Context
The legacy interview UI tightly coupled React state (useInterview) with WebSocket lifecycle and interview domain logic. This led to massive re-renders, complex testing, and an inability to support multiple layouts (coding vs. behavioral).

## Decision
We extracted all interview state, orchestration, and networking out of React into a standalone pure TypeScript `RuntimeKernel`.

## Alternatives
- Refactor useInterview with useReducer (rejected: still ties domain logic to React lifecycle).
- Redux / Zustand (rejected: requires global stores that are hard to isolate per-session).

## Tradeoffs
- Increased boilerplate for subscribing to state changes.
- Requires strict discipline to not leak React references into the runtime.

## Consequences
- The frontend is now framework-agnostic.
- The UI is purely a presentation layer that reads from snapshots.
- Sub-components can subscribe only to what they need, drastically reducing re-renders.

## Future evolution
The Runtime can be adapted to support mobile apps (React Native) or completely different frameworks without touching the core interview engine logic.