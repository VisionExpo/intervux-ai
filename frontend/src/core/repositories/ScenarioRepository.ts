import { Scenario, ScenarioProvider } from "../domain/Scenario";

export class ScenarioRepository {
    private provider: ScenarioProvider;
    private cache: Map<string, Scenario> = new Map();

    constructor(provider: ScenarioProvider) {
        this.provider = provider;
    }

    public async getScenario(id: string): Promise<Scenario> {
        if (this.cache.has(id)) {
            return this.cache.get(id)!;
        }

        const scenario = await this.provider.loadScenario(id);
        
        // Basic schema validation could go here
        if (!scenario.id || !scenario.chapters || !scenario.steps) {
            throw new Error(`Invalid scenario structure for id: ${id}`);
        }

        this.cache.set(id, scenario);
        return scenario;
    }

    public clearCache() {
        this.cache.clear();
    }
}
