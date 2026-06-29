# ADR 005: Repository Pattern for Synchronization

## Context
Connecting the Runtime modules directly to WebSocket payloads tightly couples our domain logic to the transport mechanism.

## Decision
We introduced the Repository layer (e.g., `InsightsRepository`). It listens to the network/LegacyBridge, maps DTOs into Domain Models, and stores them. The Runtime modules then subscribe to the Repository.

## Alternatives
- Modules parsing WebSocket JSON directly (rejected: brittle, couples domain to transport).

## Tradeoffs
- Requires explicit Mapper classes (e.g., `CandidateMapper`).
- One extra layer of indirection.

## Consequences
- The Runtime is entirely isolated from whether data comes from WebSockets, REST, or a local mock file.

## Future evolution
This sets the stage for Offline playback and Replay functionality, as we can simply swap the Repository implementation from a WebSocket listener to an Array iterator.