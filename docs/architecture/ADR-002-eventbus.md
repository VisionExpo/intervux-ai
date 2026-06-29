# ADR 002: EventBus Driven Architecture

## Context
Modules within the Runtime needed to share data and react to state changes without creating circular dependencies.

## Decision
We introduced a strongly typed `EventBus` as the sole communication medium between the LegacyBridge, Coordinator, and RuntimeModules.

## Alternatives
- Direct method calls between modules (rejected: high coupling, brittle).
- Global observable state (rejected: hard to track cause-and-effect).

## Tradeoffs
- Events can become difficult to trace if the bus becomes overly congested.
- Requires strict typing of event payloads to ensure safety.

## Consequences
- Modules are completely decoupled.
- We can inject an `EventRecorder` module that logs all system events for debugging and replay purposes.

## Future evolution
The EventBus will serve as the foundation for the ReplayRepository, allowing us to time-travel debug interviews by replaying the event stream.