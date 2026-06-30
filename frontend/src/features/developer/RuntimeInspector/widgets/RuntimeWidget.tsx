import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const RuntimeWidget: React.FC = () => {
    const [state, setState] = useState<any>(null);

    useEffect(() => {
        // Subscribe to EventCollector to trigger re-renders on state changes
        const unsubscribe = EventCollector.subscribe(() => {
            const kernel = (window as any).__runtimeKernel;
            if (kernel) {
                try {
                    // Try to extract state from StateModule if it exists
                    const stateModule = kernel.context.registry.getModule('StateModule');
                    if (stateModule) {
                        setState((stateModule as any).getSnapshot());
                    }
                } catch (e) {
                    // Module might not be ready
                }
            }
        });
        return unsubscribe;
    }, []);

    if (!state) return <div style={{ color: '#808080' }}>Waiting for runtime...</div>;

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178', borderBottom: '1px solid #3c3c3c', paddingBottom: '4px' }}>Interview</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: '#808080' }}>Stage</div>
                    <div style={{ color: '#4ec9b0' }}>{state.stage || 'idle'}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Question</div>
                    <div style={{ color: '#4ec9b0' }}>{state.currentQuestionIndex + 1} / {state.totalQuestions || '?'}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Speech</div>
                    <div style={{ color: '#4ec9b0' }}>{state.speechState || 'idle'}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Evaluation</div>
                    <div style={{ color: '#4ec9b0' }}>{state.evaluationState || 'idle'}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Workspace</div>
                    <div style={{ color: '#4ec9b0' }}>{state.workspaceMode || 'conversation'}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Snapshot</div>
                    <div style={{ color: '#dcdcaa' }}>#{state.version || 0}</div>
                </div>
            </div>
        </div>
    );
};
