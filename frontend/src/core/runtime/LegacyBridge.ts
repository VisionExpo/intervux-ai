import { RuntimeKernel } from './kernel/RuntimeKernel';
import { 
    InterviewStageChangedEvent, 
    QuestionUpdatedEvent, 
    EvaluationUpdatedEvent, 
} from '../events/interview/InterviewEvents';
import { ConnectionStateChangedEvent } from '../events/system/ConnectionEvents';
import { EnvelopeDeserializer } from '../transport/EnvelopeDeserializer';
import { candidateRepository } from '../repositories/CandidateProjectionRepository';

export class LegacyBridge {
    private isStarted = false;
    private kernel: RuntimeKernel;
    private sessionId: string;

    constructor(kernel: RuntimeKernel, sessionId: string) {
        this.kernel = kernel;
        this.sessionId = sessionId;
    }

    public async startIfNeeded() {
        if (!this.isStarted) {
            await this.kernel.start();
            this.isStarted = true;
        }
    }

    private deserializer = new EnvelopeDeserializer();

    public handleSocketMessage(msg: any) {
        const type = typeof msg.type === "string" ? msg.type : "";
        const normalizedType = type.toLowerCase();

        // New Backend Projection Pipeline
        if (type === "projection") {
            const rawEnvelope = msg.projection;
            if (rawEnvelope) {
                // Publish raw envelope globally for Inspector tooling
                this.kernel.context.eventBus.publish({
                    type: 'ProjectionReceived',
                    payload: rawEnvelope,
                    timestamp: Date.now()
                } as any);

                // Deserialize to Domain Model and route to Repository
                const domainModel = this.deserializer.deserialize(rawEnvelope);
                if (domainModel && rawEnvelope.schema === 'candidate-insights') {
                    candidateRepository.update(domainModel);
                }
            }
            return; // Projections don't fall through to legacy handlers
        }

        if (type === "PHASE_CHANGE" || type === "RESUMED") {
            const phase = msg.phase;
            let mappedPhase = phase;
            if (phase === "QUESTION") mappedPhase = "ASKING_QUESTION";
            if (phase === "PROCESSING") mappedPhase = "PROCESSING_ANSWER";
            if (phase === "COMPLETE") mappedPhase = "INTERVIEW_COMPLETE";

            this.kernel.context.eventBus.publish(
                new InterviewStageChangedEvent(this.sessionId, mappedPhase)
            );
        }

        if (type === "avatar_sync" || type === "question" || type === "next_question") {
            const qIndex = Number(msg.question_index ?? 0);
            const total = Number(msg.total_questions ?? 0);
            this.kernel.context.eventBus.publish(
                new QuestionUpdatedEvent(this.sessionId, qIndex, total)
            );
        }

        if (type === "evaluation") {
            this.kernel.context.eventBus.publish(
                new EvaluationUpdatedEvent(this.sessionId, msg.data)
            );
        }

        if (type === "interview_complete" || normalizedType === "complete") {
            this.kernel.context.eventBus.publish(
                new InterviewStageChangedEvent(this.sessionId, "INTERVIEW_COMPLETE")
            );
        }
    }

    public handleConnectionChange(isConnected: boolean) {
        this.kernel.context.eventBus.publish(
            new ConnectionStateChangedEvent(this.sessionId, isConnected ? 'Connected' : 'Disconnected')
        );
    }

    public verifyDivergence(legacyState: any) {
        const snapshot = this.kernel.snapshot();
        const sessionModule = snapshot['SessionModule'] || {};
        
        let diverged = false;
        
        if (legacyState.questionIndex !== sessionModule.questionIndex) {
            this.kernel.context.logger.warn(`Runtime Divergence Detected: questionIndex (Legacy: ${legacyState.questionIndex} vs Runtime: ${sessionModule.questionIndex})`);
            diverged = true;
        }
        if (legacyState.totalQuestions !== sessionModule.totalQuestions) {
            this.kernel.context.logger.warn(`Runtime Divergence Detected: totalQuestions (Legacy: ${legacyState.totalQuestions} vs Runtime: ${sessionModule.totalQuestions})`);
            diverged = true;
        }

        // Compare evaluation using JSON.stringify for deep comparison
        const legacyEvalStr = JSON.stringify(legacyState.lastEvaluation || null);
        const runtimeEvalStr = JSON.stringify(sessionModule.lastEvaluation || null);
        if (legacyEvalStr !== runtimeEvalStr) {
            this.kernel.context.logger.warn(`Runtime Divergence Detected: lastEvaluation`);
            diverged = true;
        }

        if (!diverged) {
            this.kernel.context.logger.debug(`Runtime Shadow Match (questionIndex=${sessionModule.questionIndex})`);
        }
    }
}
