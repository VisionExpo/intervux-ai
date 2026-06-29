# Architecture Decision Records (ADRs)

This file logs significant architectural decisions made during the development of Intervux.

## ADR 1: The Interview OS Architecture
*   **Date**: 2026-06-29
*   **Decision**: Transition from a page-based layout to a state-driven "Operating System" architecture where the UI is a presentation shell for an underlying `InterviewRuntime`.
*   **Rationale**: As the interview format expands (Coding, System Design, Live Debugging, Vision Analytics), a tightly coupled UI and logic layer becomes impossible to maintain. We need absolute separation of concerns.
*   **Expected Consequences**: Requires a significant initial refactoring sprint to extract logic. However, future features will be significantly easier and safer to implement.

## ADR 2: Workspace Plugin System
*   **Date**: 2026-06-29
*   **Decision**: Implement central interview areas (Coding, Conversation) as Plugins (`WorkspacePlugin`) loaded by a `WorkspaceManager`.
*   **Rationale**: The dashboard should not need to be updated every time a new interview type (e.g., SQL, Kubernetes) is introduced.
*   **Expected Consequences**: The core layout engine remains stable and small.

## ADR 3: Event Bus & Event Timeline
*   **Date**: 2026-06-29
*   **Decision**: Replace the simple "Transcript" chat UI with an `EventTimeline` backed by an internal Event Bus.
*   **Rationale**: Interviews produce diverse events (AI thoughts, candidate speech, eye contact lost, code executed). We need a unified timeline for real-time visibility, telemetry, and future interview replay.
*   **Expected Consequences**: Standardizes all system events under the `InterviewEvent` interface.
