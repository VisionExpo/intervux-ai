import { EventBus } from '../../events/EventBus';
import { Logger } from './Logger';
import { Clock } from './Clock';
import { RuntimeRegistry } from './RuntimeRegistry';

export interface RuntimeConfig {
    [key: string]: any;
}

export class RuntimeContext {
    public readonly registry: RuntimeRegistry;
    public readonly eventBus: EventBus;
    public readonly logger: Logger;
    public readonly clock: Clock;
    public readonly config: RuntimeConfig;
    public readonly telemetry?: any;

    constructor(
        registry: RuntimeRegistry,
        eventBus: EventBus,
        logger: Logger,
        clock: Clock,
        config: RuntimeConfig,
        telemetry?: any
    ) {
        this.registry = registry;
        this.eventBus = eventBus;
        this.logger = logger;
        this.clock = clock;
        this.config = config;
        this.telemetry = telemetry;
    }
}
