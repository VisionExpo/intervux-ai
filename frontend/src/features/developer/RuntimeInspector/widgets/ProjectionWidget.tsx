import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';
import { LogEntry } from '../../../../core/utils/StructuredLogger';
import { candidateRepository } from '../../../../core/repositories/CandidateProjectionRepository';
import { CandidateInsightModel, RawProjectionEnvelope } from '../../../../core/transport/EnvelopeDeserializer';

export const ProjectionWidget: React.FC = () => {
    const [lastRawEnvelope, setLastRawEnvelope] = useState<RawProjectionEnvelope | null>(null);
    const [candidateInsight, setCandidateInsight] = useState<CandidateInsightModel | null>(null);

    useEffect(() => {
        // Subscribe to raw envelopes via the EventBus/Collector
        const unsubscribeEvents = EventCollector.subscribe((latestEvents) => {
            const projEvent = latestEvents.slice().reverse().find(e => e.event === 'ProjectionReceived');
            if (projEvent && projEvent.metadata?.payload) {
                setLastRawEnvelope(projEvent.metadata.payload as RawProjectionEnvelope);
            }
        });
        
        // Subscribe to Domain Model via Repository Hook
        const unsubscribeRepo = candidateRepository.subscribe((insight) => {
            setCandidateInsight(insight);
        });

        return () => {
            unsubscribeEvents();
            unsubscribeRepo();
        };
    }, []);

    return (
        <div style={{ backgroundColor: '#252526', padding: '12px', borderRadius: '4px', border: '1px solid #3c3c3c' }}>
            <h4 style={{ margin: '0 0 12px 0', color: '#c586c0', display: 'flex', justifyContent: 'space-between' }}>
                <span>Backend Projections</span>
                {lastRawEnvelope && <span style={{ color: '#4ec9b0', fontSize: '10px' }}>v{lastRawEnvelope.projectionVersion}</span>}
            </h4>

            <div style={{ marginBottom: '16px' }}>
                <div style={{ color: '#808080', fontSize: '10px', marginBottom: '4px' }}>Domain Model (Repository State)</div>
                <div style={{ 
                    backgroundColor: '#1e1e1e', 
                    padding: '8px', 
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                    color: '#9cdcfe'
                }}>
                    {candidateInsight ? (
                        <>
                            <div>State: <span style={{ color: '#ce9178' }}>{candidateInsight.state}</span></div>
                            <div>Role: <span style={{ color: '#ce9178' }}>{candidateInsight.roleTarget}</span></div>
                            <div>Progress: <span style={{ color: '#b5cea8' }}>{candidateInsight.progress.currentQuestionIndex}/{candidateInsight.progress.totalQuestionsAsked}</span></div>
                        </>
                    ) : (
                        <span style={{ color: '#808080' }}>Waiting for insights...</span>
                    )}
                </div>
            </div>

            <div>
                <div style={{ color: '#808080', fontSize: '10px', marginBottom: '4px' }}>Raw Envelope (Transport)</div>
                {lastRawEnvelope ? (
                    <pre style={{ 
                        margin: 0, 
                        padding: '8px', 
                        backgroundColor: '#1e1e1e', 
                        fontSize: '10px', 
                        overflowX: 'auto',
                        borderRadius: '4px',
                        color: '#dcdcaa'
                    }}>
                        {JSON.stringify(lastRawEnvelope, null, 2)}
                    </pre>
                ) : (
                    <div style={{ backgroundColor: '#1e1e1e', padding: '8px', borderRadius: '4px', color: '#808080', fontSize: '10px' }}>
                        No envelopes received
                    </div>
                )}
            </div>
        </div>
    );
};
