import { Scenario } from "../../domain/Scenario";
import { StoryStep, StoryCommand } from "../../domain/StoryStep";
import { RuntimeContext } from "../kernel/RuntimeContext";
import { ScenarioRepository } from "../../repositories/ScenarioRepository";

export class StoryEngine {
    private context: RuntimeContext;
    private repository: ScenarioRepository;
    private currentScenario: Scenario | null = null;
    private stepIndex: number = 0;
    private isRunning: boolean = false;
    private pendingStep: StoryStep | null = null;
    public commandHistory: { timestamp: number; command: StoryCommand }[] = [];

    constructor(context: RuntimeContext, repository: ScenarioRepository) {
        this.context = context;
        this.repository = repository;
    }

    public async loadAndStart(scenarioId: string) {
        this.currentScenario = await this.repository.getScenario(scenarioId);
        this.restart();
    }

    public restart() {
        this.stepIndex = 0;
        this.commandHistory = [];
        this.pendingStep = null;
        this.isRunning = true;
        this.context.logger.info(`[StoryEngine] Started/Restarted scenario`);
        this.context.eventBus.subscribeAll(this.handleRuntimeEvent.bind(this));
        this.executeNextStep();
    }

    public stop() {
        this.isRunning = false;
        this.pendingStep = null;
        this.context.logger.info("[StoryEngine] Stopped execution.");
    }

    public pause() {
        this.isRunning = false;
        this.context.logger.info("[StoryEngine] Paused.");
        this.context.clock.pause();
    }

    public resume() {
        this.isRunning = true;
        this.context.logger.info("[StoryEngine] Resumed.");
        this.context.clock.resume();
        if (this.pendingStep) {
            // Already waiting for an event
            return;
        }
        this.executeNextStep();
    }

    public step() {
        if (!this.currentScenario || this.stepIndex >= this.currentScenario.steps.length) return;
        const step = this.currentScenario.steps[this.stepIndex];
        this.dispatchCommand(step);
    }

    public seek(chapterId: string) {
        if (!this.currentScenario) return;
        const index = this.currentScenario.steps.findIndex(s => s.chapterId === chapterId);
        if (index !== -1) {
            this.stepIndex = index;
            this.pendingStep = null;
            this.context.logger.info(`[StoryEngine] Seeked to chapter ${chapterId} (step ${index})`);
            if (this.isRunning) this.executeNextStep();
        }
    }

    private executeNextStep() {
        if (!this.isRunning || !this.currentScenario) return;

        if (this.stepIndex >= this.currentScenario.steps.length) {
            this.context.logger.info("[StoryEngine] Scenario completed.");
            this.stop();
            return;
        }

        const step = this.currentScenario.steps[this.stepIndex];
        
        if (step.waitFor) {
            this.pendingStep = step;
            this.context.logger.info(`[StoryEngine] Step ${step.id} waiting for event: ${step.waitFor}`);
            return;
        }

        this.dispatchCommand(step);
    }

    private dispatchCommand(step: StoryStep) {
        this.context.logger.info(`[StoryEngine] Executing step ${step.id}: ${step.command.type}`);
        
        this.commandHistory.push({
            timestamp: this.context.clock.now(),
            command: step.command
        });

        this.context.eventBus.emit(step.command.type, step.command.payload);

        this.stepIndex++;
        this.executeNextStep();
    }

    private handleRuntimeEvent(eventName: string, payload: any) {
        if (!this.isRunning || !this.pendingStep) return;

        if (this.pendingStep.waitFor === eventName) {
            this.context.logger.info(`[StoryEngine] Wait condition met: ${eventName} for step ${this.pendingStep.id}`);
            const stepToExecute = this.pendingStep;
            this.pendingStep = null;
            this.dispatchCommand(stepToExecute);
        }
    }

    public getState() {
        return {
            scenario: this.currentScenario?.title || null,
            currentStep: this.currentScenario?.steps[this.stepIndex - 1]?.id || null,
            nextStep: this.currentScenario?.steps[this.stepIndex]?.id || null,
            waitingFor: this.pendingStep?.waitFor || null,
            isRunning: this.isRunning,
            historyLength: this.commandHistory.length
        };
    }
}
