import { RuntimeModule, ModuleHealth } from "./RuntimeModule";
import { RuntimeContext } from "../kernel/RuntimeContext";
import { DomainEvent } from "../../events/DomainEvent";
import { WorkspaceType, WorkspaceState, WorkspaceTransition, TransitionReason, TransitionAnimation } from "../../domain/Workspace";

export class WorkspaceModule implements RuntimeModule {
    public readonly id = "workspace_module";
    private context!: RuntimeContext;
    private state: WorkspaceState;
    private _health: ModuleHealth = "initializing";

    constructor() {
        this.state = {
            activeWorkspace: "system", // Start in system for prep
            isTransitioning: false,
        };
    }

    public async initialize(context: RuntimeContext): Promise<void> {
        this.context = context;
        this._health = "healthy";
        this.context.eventBus.subscribe("WorkspaceTransitionRequested", this.handleTransitionRequest.bind(this));
        console.log(`[${this.id}] Initialized`);
    }

    public async start(): Promise<void> {
        // Module started
    }

    public async stop(): Promise<void> {
        // Module stopped
    }

    public async dispose(): Promise<void> {
        // Module disposed
    }

    public async handle(event: DomainEvent): Promise<void> {
        // Handled via explicit subscription mapping above to maintain strong typing
    }

    public health(): ModuleHealth {
        return this._health;
    }

    public snapshot(): WorkspaceState {
        return { ...this.state };
    }

    public getActiveWorkspace(): WorkspaceType {
        return this.state.activeWorkspace;
    }

    // Command API: Only WorkspaceModule is allowed to transition workspaces.
    public async transition(to: WorkspaceType, reason: TransitionReason, animation: TransitionAnimation = "fade"): Promise<void> {
        if (this.state.isTransitioning || this.state.activeWorkspace === to) {
            return;
        }

        const transition: WorkspaceTransition = {
            from: this.state.activeWorkspace,
            to,
            reason,
            animation
        };

        this.state.isTransitioning = true;
        this.state.lastTransition = transition;
        
        this.context.eventBus.emit("WorkspaceTransitionStarted", { transition });

        // Simulate animation/transition latency
        // Later this can be tied to actual React animation completions via callback
        await new Promise(resolve => setTimeout(resolve, 300));

        this.state.activeWorkspace = to;
        this.state.isTransitioning = false;

        this.context.eventBus.emit("WorkspaceTransitionCompleted", { transition });
    }

    private async handleTransitionRequest(payload: any) {
        if (payload?.to && payload?.reason) {
            await this.transition(payload.to as WorkspaceType, payload.reason as TransitionReason, payload.animation);
        } else {
            this.context.eventBus.emit("WorkspaceTransitionFailed", { error: "Invalid transition payload" });
        }
    }
}
