import type { RuntimeModule } from '../modules/RuntimeModule';
import { RuntimeContext } from './RuntimeContext';
import { Logger } from './Logger';

export class RuntimeRegistry {
    private modules: Map<string, RuntimeModule> = new Map();

    public register(module: RuntimeModule): void {
        if (this.modules.has(module.id)) {
            throw new Error(`Module with id ${module.id} is already registered.`);
        }
        this.modules.set(module.id, module);
    }

    public resolve<T extends RuntimeModule>(id: string): T {
        const module = this.modules.get(id);
        if (!module) {
            throw new Error(`Module with id ${id} not found in registry.`);
        }
        return module as T;
    }

    public async initializeAll(context: RuntimeContext): Promise<void> {
        context.logger.info("Initializing all modules...");
        for (const module of this.modules.values()) {
            await module.initialize(context);
        }
    }

    public async startAll(logger: Logger): Promise<void> {
        logger.info("Starting all modules...");
        for (const module of this.modules.values()) {
            await module.start();
        }
    }

    public async stopAll(logger: Logger): Promise<void> {
        logger.info("Stopping all modules...");
        for (const module of this.modules.values()) {
            await module.stop();
        }
    }

    public async disposeAll(logger: Logger): Promise<void> {
        logger.info("Disposing all modules...");
        for (const module of this.modules.values()) {
            await module.dispose();
        }
        this.modules.clear();
    }
}
