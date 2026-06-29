# ADR 006: Runtime Modules

## Context
A monolithic RuntimeKernel would eventually become a God Object orchestrating all interview features (STT, TTS, Adaptive, Memory, UI state).

## Decision
We structured the Runtime into isolated `RuntimeModules` (e.g., `SessionModule`, `InterviewInsightsModule`). Each module handles a specific domain concern and communicates exclusively via the `EventBus`.

## Alternatives
- Single massive state store (rejected: poor separation of concerns).

## Tradeoffs
- Cross-module coordination must go through the Coordinator or EventBus, avoiding direct reads.

## Consequences
- Teams can build new capabilities (e.g., VisionModule for eye-tracking) without risking regressions in the core SessionModule.

## Future evolution
Modules can be dynamically loaded or disabled based on `PlatformCapabilities` feature flags.