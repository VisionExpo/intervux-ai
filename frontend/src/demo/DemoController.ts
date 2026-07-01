import { DemoScenario } from "./types";
import { EventBus } from "../core/runtime/events/EventBus";

export class DemoController {
  private eventBus: EventBus;
  private currentScenario: DemoScenario | null = null;
  private timeouts: ReturnType<typeof setTimeout>[] = [];
  private isRunning: boolean = false;

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
  }

  public loadScenario(scenario: DemoScenario) {
    this.currentScenario = scenario;
    this.stop(); // Clear any existing runs
  }

  public start() {
    if (!this.currentScenario) {
      console.warn("[DemoController] Cannot start: No scenario loaded");
      return;
    }

    if (this.isRunning) {
      console.warn("[DemoController] Already running");
      return;
    }

    this.isRunning = true;
    console.log(`[DemoController] Starting scenario: ${this.currentScenario.title}`);

    // Schedule all events based on their defined delays
    for (const event of this.currentScenario.events) {
      const timeoutId = setTimeout(() => {
        if (!this.isRunning) return;
        
        console.log(`[DemoController] Emitting scheduled event: ${event.event_type}`, event.payload);
        this.eventBus.emit(event.event_type, event.payload);
      }, event.trigger_delay_ms);

      this.timeouts.push(timeoutId);
    }
  }

  public stop() {
    this.isRunning = false;
    for (const timeoutId of this.timeouts) {
      clearTimeout(timeoutId);
    }
    this.timeouts = [];
    console.log("[DemoController] Stopped scenario execution");
  }
}
