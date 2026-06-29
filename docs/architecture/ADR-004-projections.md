# ADR 004: Projection Pipeline

## Context
The backend Adaptive Engine generates complex reasoning (Knowledge Graphs, Difficulty Calibration). Sending this raw state to the candidate's browser risks leaking the AI's strategy and compromising the interview.

## Decision
We implemented a server-side `ProjectionPipeline` (Registry & Factory pattern) that transforms the raw `InterviewAggregate` into audience-specific DTOs (CandidateDTO, RecruiterDTO, DeveloperDTO).

## Alternatives
- Frontend filtering (rejected: insecure, candidate can inspect WebSocket frames).
- Separate WebSockets (rejected: overly complex for initial phase).

## Tradeoffs
- Backend must maintain multiple mapping schemas for the same internal state.
- Increased server-side processing slightly.

## Consequences
- The candidate only receives progress indicators, while developers and recruiters receive full telemetry. Security is guaranteed at the transport layer.

## Future evolution
We can trivially add new projections (e.g., `CoachProjection`, `AnalyticsProjection`) without modifying the core engine or disrupting existing clients.