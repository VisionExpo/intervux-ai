import React from 'react';

// ============================================================================
// State Machines
// ============================================================================

export enum InterviewState {
    IDLE = 'IDLE',
    RESUME_UPLOAD = 'RESUME_UPLOAD',
    GREETING = 'GREETING',
    QUESTION_ASKED = 'QUESTION_ASKED',
    LISTENING = 'LISTENING',
    PROCESSING = 'PROCESSING',
    EVALUATING = 'EVALUATING',
    THINKING = 'THINKING',
    SPEAKING = 'SPEAKING',
    NEXT_QUESTION = 'NEXT_QUESTION',
    FINISHED = 'FINISHED'
}

export enum AIState {
    IDLE = 'IDLE',
    THINKING = 'THINKING',
    GENERATING = 'GENERATING',
    EVALUATING = 'EVALUATING',
    SYNTHESIZING = 'SYNTHESIZING',
    SPEAKING = 'SPEAKING',
    WAITING = 'WAITING'
}

export enum ConnectionState {
    DISCONNECTED = 'DISCONNECTED',
    CONNECTING = 'CONNECTING',
    CONNECTED = 'CONNECTED',
    ERROR = 'ERROR'
}

// ============================================================================
// Core Entities
// ============================================================================

export interface Question {
    id: string;
    index: number;
    text: string;
    type: 'behavioral' | 'technical' | 'coding' | 'system_design';
}

export interface CandidateProfile {
    id: string;
    name: string;
    skills: string[];
    experience: string[];
}

// ============================================================================
// Event Timeline (Event Bus)
// ============================================================================

export type EventSeverity = 'info' | 'success' | 'warning' | 'error';

export interface InterviewEvent<T = any> {
    id: string;
    timestamp: number;
    type: string; // e.g., 'SpeechStarted', 'FaceLost', 'QuestionAsked'
    source: 'system' | 'ai' | 'candidate' | 'vision' | 'evaluation';
    payload: T;
    severity: EventSeverity;
}

// ============================================================================
// Sub-States
// ============================================================================

export interface MediaState {
    isMicActive: boolean;
    isCameraActive: boolean;
    audioLevel: number; // 0-100 for noise level visualization
    recordingDurationSec: number;
}

export interface VisionState {
    faceVisible: boolean;
    eyeContact: boolean;
    cameraStable: boolean;
    lookingAway: boolean;
    multipleFaces: boolean;
    lightingGood: boolean;
    headPose: 'forward' | 'up' | 'down' | 'left' | 'right';
    phoneDetected: boolean;
    isSpeaking: boolean;
}

export interface WorkspaceConfiguration {
    layout: 'conversation' | 'coding' | 'debugging' | 'system-design' | 'whiteboard' | 'review';
    showEventTimeline: boolean;
    showSandbox: boolean;
    showVisionPanel: boolean;
    showQuestionCard: boolean;
    showVoiceControls: boolean;
}

// ============================================================================
// Root State (InterviewRuntimeState)
// ============================================================================

export interface InterviewRuntimeState {
    interviewState: InterviewState;
    aiState: AIState;
    connectionState: ConnectionState;

    currentQuestion: Question | null;
    totalQuestions: number;
    
    candidate: CandidateProfile | null;
    
    workspace: WorkspaceConfiguration;
    
    media: MediaState;
    vision: VisionState;
    
    events: InterviewEvent[];
}

// ============================================================================
// Plugin System
// ============================================================================

export interface Shortcut {
    key: string;
    description: string;
    action: () => void;
}

export interface Command {
    id: string;
    label: string;
    execute: () => void;
}

export interface WorkspacePlugin {
    id: string; // e.g., 'CodingWorkspace'
    
    // Core render methods
    render: () => React.ReactNode;
    toolbar: () => React.ReactNode;
    
    // Extensibility
    shortcuts: () => Shortcut[];
    commands: () => Command[];
    
    // Lifecycle
    cleanup: () => void;
}
