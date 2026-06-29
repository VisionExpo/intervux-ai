export const capabilities = {
    // Core Platform
    dashboard: true,
    coding: true,
    voice: true,

    // AI Intelligence
    adaptive: false,
    analytics: false,
    vision: false,

    // Developer / Platform
    telemetry: false,
    developer: false,
    replay: false,
    plugins: false,
    experiments: false,
};

export type PlatformCapabilities = typeof capabilities;

export const isCapabilityEnabled = (capability: keyof PlatformCapabilities): boolean => {
    return capabilities[capability];
};
