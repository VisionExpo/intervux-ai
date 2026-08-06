# ADR-008: Interview Aggregate

## Status
Accepted

## Context
As the Intervux platform grows, the state of an interview has become fragmented across various database tables, websocket session states, and frontend components. This fragmentation leads to:
1. Difficulties in deterministic replay.
2. Complicated event sourcing and projections.
3. Mutations that bypass business rules.
4. "Published-but-not-saved" bugs where domain events are emitted before persistence succeeds.

To prepare for the Projection Pipeline and Adaptive Backend capabilities, we need a single, consistent source of truth for the lifecycle of an interview.

## Decision
We will introduce the `InterviewAggregate` as the central Aggregate Root within a feature-modular Domain-Driven Design (DDD) architecture. All state mutations regarding an interview must strictly pass through this aggregate.

### Purpose
The aggregate exists to:
- Centralize all interview state mutations.
- Enforce strict business invariants and lifecycle progression.
- Decouple the domain model from transport (WebSockets), persistence (PostgreSQL/Redis), and presentation (React).
- Act as the singular generator of immutable Domain Events (event sourcing foundation).

### Aggregate Boundaries
Explicitly defining what belongs inside the aggregate and what does not.

**The Aggregate OWNS:**
- Candidate profile & Resume details
- Session metadata
- Conversation timeline & Transcript history
- Adaptive Engine State & Coverage metrics
- Evaluation payload & Memory 
- Current Version
- Pending Domain Events queue

**The Aggregate NEVER OWNS:**
- WebSocket connections or socket IDs
- Redis or PostgreSQL clients
- Projection DTOs (e.g., GraphQL responses or REST models)
- Runtime/StoryEngine logic
- AI Model Clients (e.g., OpenAI/Anthropic SDKs)
- Repositories

### Versioning
We will utilize **Optimistic Versioning**. Every state mutation on the aggregate will strictly increment its internal version number (e.g., Version 7 -> Mutation -> Version 8). Repositories must enforce version parity to reject stale saves.

### Domain Events
The aggregate will not immediately publish events. Instead, it will append immutable events (e.g., `InterviewStarted`, `QuestionAsked`) to an internal `pending_events` list. The Application Service is responsible for extracting and publishing these events *only after* the aggregate has been successfully persisted by the repository.

## Consequences
- **Positive**: We achieve strict consistency, testability, and a clear path toward the Projection Pipeline.
- **Negative**: Adds a layer of indirection (Application Service -> Command -> Aggregate -> Repository) compared to direct CRUD operations.
