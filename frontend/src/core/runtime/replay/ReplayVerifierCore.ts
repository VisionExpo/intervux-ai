import { RuntimeKernel } from "../kernel/RuntimeKernel";
import { DemoSessionReplay } from "./ReplayTypes";
import { SnapshotHasher } from "./SnapshotHasher";
import { ReplayMismatchError } from "./ReplayMismatch";

export class ReplayVerifierCore {
    private kernel: RuntimeKernel;
    private session: DemoSessionReplay;

    constructor(kernel: RuntimeKernel, session: DemoSessionReplay) {
        this.kernel = kernel;
        this.session = session;
    }

    public async verify(): Promise<boolean> {
        for (const tick of this.session.timeline) {
            
            // 1. Verify Command OR Event Hash parity BEFORE executing
            if (tick.command) {
                const commandHash = await SnapshotHasher.hash(tick.command);
                if (commandHash !== tick.commandHash) {
                    throw new ReplayMismatchError(tick.tick, "command", tick.commandHash!, commandHash);
                }
                
                // Dispatch Command
                this.kernel.context.eventBus.emit(tick.command.type, tick.command.payload);
            } 
            else if (tick.event) {
                const eventHash = await SnapshotHasher.hash(tick.event);
                if (eventHash !== tick.eventHash) {
                    throw new ReplayMismatchError(tick.tick, "event", tick.eventHash!, eventHash);
                }

                // Dispatch Event
                this.kernel.context.eventBus.emit(tick.event.type, tick.event.payload);
            }

            // 2. Verify Snapshot parity AFTER executing
            const actualSnapshotHash = await SnapshotHasher.hash(this.kernel.snapshot());
            if (actualSnapshotHash !== tick.snapshotHash) {
                throw new ReplayMismatchError(tick.tick, "snapshot", tick.snapshotHash, actualSnapshotHash);
            }
        }

        return true;
    }
}
