export interface DemoScenario {
  scenario_id: string;
  title: string;
  candidate: {
    name: string;
    role_target: string;
    experience_level: string;
  };
  journey: {
    stages: Array<{
      id: string;
      title: string;
      workspace: "conversation" | "coding" | "whiteboard" | "system";
      status: "completed" | "current" | "upcoming";
    }>;
  };
  events: Array<{
    trigger_delay_ms: number;
    event_type: string;
    payload: any;
  }>;
  completionReport: any;
}
