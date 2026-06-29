# Interview Dashboard

## Purpose
The `InterviewDashboard` is a pure presentation component. It contains zero business logic and does not communicate with external services (no WebSockets, no Media APIs).

## Principles
1. **Dumb Rendering**: It only renders the state passed down by the `InterviewRuntime`.
2. **Adaptive Grid**: It uses CSS Grid to arrange its panels (TopBar, Sidebar, Center Workspace, BottomBar) based on the `WorkspaceConfiguration`.
3. **No Replacements**: It relies on overlays or smooth transitions rather than completely replacing pages to avoid jarring context switches.

## Component Hierarchy
```
Dashboard
├── TopNavigation
├── LeftSidebar
├── WorkspaceManager (Loads Plugins)
├── EventTimeline
└── BottomStatusBar
```
