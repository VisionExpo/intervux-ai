export interface ReplayTimelineTick {
    tick: number;
    command?: { type: string; payload?: any };
    commandHash?: string;
    event?: { type: string; payload?: any };
    eventHash?: string;
    snapshotHash: string;
}

export interface ReplayPlatformData {
    browser?: string;
    frontend: string;
    backend?: string;
}

export interface DemoSessionReplay {
    schema: string;
    runtimeVersion: string;
    scenario: string;
    seed: number;
    generatedAt: string;
    platform: ReplayPlatformData;
    timeline: ReplayTimelineTick[];
}
