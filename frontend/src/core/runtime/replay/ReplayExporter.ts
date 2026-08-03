import { RuntimeKernel } from "../kernel/RuntimeKernel";
import { DemoSessionReplay, ReplayTimelineTick } from "./ReplayTypes";
import { SnapshotHasher } from "./SnapshotHasher";

export class ReplayExporter {
    private kernel: RuntimeKernel;
    private timeline: ReplayTimelineTick[] = [];
    private tickCount = 0;

    constructor(kernel: RuntimeKernel) {
        this.kernel = kernel;
    }

    public startObservation() {
        this.timeline = [];
        this.tickCount = 0;
        // In a complete implementation, this would subscribe to the EventBus
        // intercepting both raw events and commands. For demonstration, we expose
        // explicit record hooks that StoryEngine or EventBus would call.
    }

    public async recordCommand(commandType: string, payload: any) {
        this.tickCount++;
        const commandPayload = { type: commandType, payload };
        const commandHash = await SnapshotHasher.hash(commandPayload);
        const snapshotHash = await SnapshotHasher.hash(this.kernel.snapshot());

        this.timeline.push({
            tick: this.tickCount,
            command: commandPayload,
            commandHash,
            snapshotHash
        });
    }

    public async recordEvent(eventType: string, payload: any) {
        this.tickCount++;
        const eventPayload = { type: eventType, payload };
        const eventHash = await SnapshotHasher.hash(eventPayload);
        const snapshotHash = await SnapshotHasher.hash(this.kernel.snapshot());

        this.timeline.push({
            tick: this.tickCount,
            event: eventPayload,
            eventHash,
            snapshotHash
        });
    }

    public exportSession(scenarioId: string, seed: number): DemoSessionReplay {
        return {
            schema: "intervux-replay-v1",
            runtimeVersion: "1.0.0",
            scenario: scenarioId,
            seed,
            generatedAt: new Date().toISOString(),
            platform: {
                browser: typeof navigator !== 'undefined' ? navigator.userAgent : "Node.js",
                frontend: "React/18"
            },
            timeline: this.timeline
        };
    }
}
