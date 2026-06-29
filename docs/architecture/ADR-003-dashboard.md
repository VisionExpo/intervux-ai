# ADR 003: Dashboard Shell and Adapters

## Context
The UI needed to support vastly different layouts (e.g., Conversation vs. Coding) while sharing the same underlying state and camera/audio components.

## Decision
We introduced a `DashboardShell` layout component and a layer of UI Adapters (`QuestionCardAdapter`, `CandidateMonitorAdapter`). The Adapters read from the Runtime and feed pure UI widgets.

## Alternatives
- Monolithic conditional rendering inside one huge InterviewPage (rejected: unmaintainable).
- Completely separate pages for Coding vs Conversation (rejected: loses camera/audio state across navigations).

## Tradeoffs
- Requires creating an Adapter for every widget.
- Slightly deeper component trees.

## Consequences
- Layouts are highly modular. We can instantly switch between a coding interface and a behavioral interface without remounting the camera or WebSocket.

## Future evolution
This allows us to dynamically inject new widgets (e.g., Adaptive Insights for recruiters) seamlessly via configuration.