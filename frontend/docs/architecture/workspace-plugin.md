# Workspace Plugins

## Purpose
To allow the Interview OS to scale to numerous interview formats (Whiteboarding, Code Execution, SQL, Kubernetes) without bloating the core dashboard.

## Concept
A `WorkspacePlugin` defines a standard interface:
```ts
interface WorkspacePlugin {
    id: string;
    render(): React.ReactNode;
    toolbar(): React.ReactNode;
    shortcuts(): Shortcut[];
    commands(): Command[];
    cleanup(): void;
}
```

The Dashboard's `WorkspaceManager` simply loads the active plugin based on the `WorkspaceConfiguration`. New interview modes can be dropped into the `plugins/` directory and registered without modifying the layout engine.
