export interface RawProjectionEnvelope {
    schema: string;
    schemaVersion: number;
    aggregateVersion: number;
    projectionVersion: number;
    payload: any;
}

export interface CandidateInsightModel {
    candidateName: string;
    roleTarget: string;
    state: string;
    progress: {
        currentQuestionIndex: number;
        totalQuestionsAsked: number;
    };
    version: number;
}

export class EnvelopeDeserializer {
    public deserialize(rawMsg: any): any {
        if (!rawMsg || !rawMsg.schema) return null;
        
        switch (rawMsg.schema) {
            case 'candidate-insights':
                return this.mapToCandidateInsight(rawMsg);
            case 'developer-debug':
                return rawMsg; // For debug, pass raw
            case 'telemetry-heartbeat':
                return rawMsg;
            default:
                console.warn(`Unknown projection schema: ${rawMsg.schema}`);
                return null;
        }
    }
    
    private mapToCandidateInsight(envelope: RawProjectionEnvelope): CandidateInsightModel {
        return {
            candidateName: envelope.payload.candidateName || "Unknown",
            roleTarget: envelope.payload.roleTarget || "Unknown",
            state: envelope.payload.state || "Unknown",
            progress: {
                currentQuestionIndex: envelope.payload.progress?.currentQuestionIndex || 0,
                totalQuestionsAsked: envelope.payload.progress?.totalQuestionsAsked || 0
            },
            version: envelope.projectionVersion
        };
    }
}
