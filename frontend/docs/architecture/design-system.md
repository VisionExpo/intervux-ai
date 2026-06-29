# Design System & UX Principles

## Principles
1. **One Primary Focus**: The UI must adapt to highlight the most critical tool for the current phase (e.g., Editor for coding, Conversation for behavioral).
2. **No Surprises**: The dashboard uses smooth transitions and overlays. Panels do not jump or disappear unexpectedly.
3. **Always Visible Controls**: Essential controls (End Interview, Mic, Camera, Connection, Recording, Timer) are permanently pinned.
4. **Transparent AI**: The candidate must always know what the AI is doing (Analyzing, Generating, Speaking) via clear visual indicators.
5. **Single Primary CTA**: Never present competing primary actions (e.g., "Done Speaking" is the sole primary CTA when answering).

## Implementation
All components must use `ThemeTokens` from the design system, never hardcoded utility classes. Components provide robust variants (primary, secondary, ghost, danger).
