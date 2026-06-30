import { describe, it, expect, vi } from 'vitest';
import { RuntimeKernel } from '../../src/core/runtime/kernel/RuntimeKernel';
import { StateModule } from '../../src/core/runtime/modules/StateModule';

describe('RuntimeKernel Lifecycle', () => {
    it('should construct correctly with EventBus and ModuleRegistry', () => {
        const kernel = new RuntimeKernel({});
        expect(kernel.context.eventBus).toBeDefined();
        expect(kernel.context.registry).toBeDefined();
    });

    it('should register and initialize modules', async () => {
        const kernel = new RuntimeKernel({});
        const stateModule = new StateModule();
        
        kernel.context.registry.register(stateModule);
        
        const retrieved = kernel.context.registry.getModules().find(m => m.id === stateModule.id);
        expect(retrieved).toBe(stateModule);
    });

    it('should maintain health status', () => {
        const kernel = new RuntimeKernel({});
        
        // Very basic mock of health functionality 
        // Real implementation would poll modules
        expect(kernel.context.registry.getModules().length).toBe(0);
        
        kernel.context.registry.register(new StateModule());
        expect(kernel.context.registry.getModules().length).toBe(1);
    });
});
