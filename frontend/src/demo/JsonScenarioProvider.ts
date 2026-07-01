import { Scenario, ScenarioProvider } from "../core/domain/Scenario";

export class JsonScenarioProvider implements ScenarioProvider {
    public async loadScenario(id: string): Promise<Scenario> {
        try {
            // In a real app, this might be a dynamic import or fetch
            // For the demo, we statically require or fetch from a public URL
            
            // To simulate network latency and demonstrate waiting states
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Simulate reading from our created json file (which is in the same directory but we will fetch it as a mock)
            // Note: During local dev, you'd fetch from public folder or import directly.
            // Using a dynamic import for simplicity in React/Vite/Webpack
            const module = await import(`./scenarios/${id}.json`);
            return module.default as Scenario;
        } catch (error) {
            console.error(`Failed to load scenario ${id}`, error);
            throw new Error(`Scenario ${id} not found.`);
        }
    }
}
