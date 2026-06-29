// ============================================================================
// Feature Flags
// ============================================================================

export const features = {
    // Advanced Interview Modes
    newDashboard: false,
    developerWorkspace: true,
    systemDesignWorkspace: false,
    
    // UI/UX
    thinkingAnimation: true,
    orbAvatar: true,
    vrmAvatar: false,
    richVoiceControls: true,
    
    // Future Analytics / Capabilities
    vision: false, // Eye tracking, cheating detection, etc.
    replay: false, // Interview timeline replay
    liveScoring: false,
};

export type Features = typeof features;

export const isFeatureEnabled = (feature: keyof Features): boolean => {
    return features[feature];
};
