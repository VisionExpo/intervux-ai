# Layout Engine

## Purpose
The Layout Engine abstracts the visual arrangement of the dashboard from the interview logic.

## Concept
Instead of hardcoding "Coding Page" or "Behavioral Page", the engine receives a `WorkspaceConfiguration`:

```ts
interface WorkspaceConfiguration {
    layout: "conversation" | "coding" | "system-design";
    showEventTimeline: boolean;
    showSandbox: boolean;
    // ...
}
```

The engine then maps this configuration to CSS Grid templates. This allows us to instantly change the workspace layout (e.g., maximizing the coding sandbox) simply by mutating the state configuration.
