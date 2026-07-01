export type WorkspaceType = "conversation" | "coding" | "whiteboard" | "system";

export type TransitionReason = "chapter" | "question" | "system" | "manual";
export type TransitionAnimation = "fade" | "slide" | "expand";

export interface WorkspaceTransition {
    from: WorkspaceType;
    to: WorkspaceType;
    reason: TransitionReason;
    animation?: TransitionAnimation;
}

export interface WorkspaceState {
    activeWorkspace: WorkspaceType;
    isTransitioning: boolean;
    lastTransition?: WorkspaceTransition;
}
