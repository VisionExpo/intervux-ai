import { RuntimeContext, type RuntimeConfig } from './RuntimeContext';
import { RuntimeRegistry } from './RuntimeRegistry';
import { EventBus } from '../../events/EventBus';
import { Logger } from './Logger';
import { Clock } from './Clock';
import { Coordinator } from '../coordinator/Coordinator';

export class RuntimeKernel {
    public readonly context: RuntimeContext;
    private coordinator: Coordinator;

    constructor(config: RuntimeConfig) {
        const registry = new RuntimeRegistry();
        const eventBus = new EventBus();
        const logger = new Logger();
        const clock = new Clock();

        this.context = new RuntimeContext(
            registry,
            eventBus,
            logger,
            clock,
            config
        );

        this.coordinator = new Coordinator(this.context);
    }

    public async start(): Promise<void> {
        this.context.logger.info("Starting RuntimeKernel...");
        await this.context.registry.initializeAll(this.context);
        await this.coordinator.start();
        await this.context.registry.startAll(this.context.logger);
        this.context.logger.info("RuntimeKernel started.");
    }

    public async stop(): Promise<void> {
        this.context.logger.info("Stopping RuntimeKernel...");
        await this.coordinator.stop();
        await this.context.registry.stopAll(this.context.logger);
        await this.context.registry.disposeAll(this.context.logger);
        this.context.logger.info("RuntimeKernel stopped.");
    }

    public snapshot(): any {
        const snap: any = {};
        for (const module of this.context.registry.getModules()) {
            if (module.snapshot) {
                snap[module.id] = module.snapshot();
            }
        }
        return snap;
    }

    public inspect(): any {
        return {
            version: "1.0.0",
            modules: this.context.registry.getModules().map(m => ({
                id: m.id,
                health: m.health(),
                hasSnapshot: !!m.snapshot
            }))
        };
    }
}
