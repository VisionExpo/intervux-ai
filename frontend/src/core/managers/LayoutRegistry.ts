import type { WorkspacePlugin } from '../../domain/contracts';

// ============================================================================
// Layout Registry
// ============================================================================

class LayoutRegistryClass {
    private plugins: Map<string, WorkspacePlugin> = new Map();

    register(layoutId: string, plugin: WorkspacePlugin) {
        if (this.plugins.has(layoutId)) {
            console.warn(`Plugin for layout '${layoutId}' is already registered. Overwriting.`);
        }
        this.plugins.set(layoutId, plugin);
        console.log(`Registered workspace plugin: ${layoutId}`);
    }

    get(layoutId: string): WorkspacePlugin | undefined {
        return this.plugins.get(layoutId);
    }

    getAll(): WorkspacePlugin[] {
        return Array.from(this.plugins.values());
    }
}

export const LayoutRegistry = new LayoutRegistryClass();
