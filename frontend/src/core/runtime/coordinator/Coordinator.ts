import { RuntimeContext } from '../kernel/RuntimeContext';

export class Coordinator {
    private context: RuntimeContext;
    
    constructor(context: RuntimeContext) {
        this.context = context;
    }

    public async start(): Promise<void> {
        this.context.logger.info("Coordinator started.");
        // Wires up global event listeners if necessary, routing them to the registry
    }

    public async stop(): Promise<void> {
        this.context.logger.info("Coordinator stopped.");
    }
}
