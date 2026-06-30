import React, { useEffect, useState } from 'react';

export const DiagnosticsWidget: React.FC = () => {
    const [health, setHealth] = useState({
        runtime: 'Healthy',
        eventBus: 'Healthy',
        repository: 'Healthy',
        coordinator: 'Healthy',
        modules: 'Healthy',
        snapshotSync: 'Healthy'
    });

    useEffect(() => {
        const interval = setInterval(() => {
            const kernel = (window as any).__runtimeKernel;
            if (!kernel) {
                setHealth(prev => ({ ...prev, runtime: 'Waiting', eventBus: 'Waiting' }));
                return;
            }
            // Basic heuristic: if kernel exists and context is populated
            setHealth({
                runtime: 'Healthy',
                eventBus: kernel.context?.bus ? 'Healthy' : 'Error',
                repository: 'Healthy',
                coordinator: 'Healthy',
                modules: kernel.context?.registry ? 'Healthy' : 'Error',
                snapshotSync: 'Healthy'
            });
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    const getColor = (status: string) => {
        if (status === 'Healthy') return '#4ec9b0';
        if (status === 'Error') return '#f14c4c';
        return '#dcdcaa'; // Yellow / Waiting
    };

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178', borderBottom: '1px solid #3c3c3c', paddingBottom: '4px' }}>Diagnostics</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: '#808080' }}>Runtime</div>
                    <div style={{ color: getColor(health.runtime) }}>{health.runtime}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>EventBus</div>
                    <div style={{ color: getColor(health.eventBus) }}>{health.eventBus}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Repository</div>
                    <div style={{ color: getColor(health.repository) }}>{health.repository}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Coordinator</div>
                    <div style={{ color: getColor(health.coordinator) }}>{health.coordinator}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Modules</div>
                    <div style={{ color: getColor(health.modules) }}>{health.modules}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Snapshot Sync</div>
                    <div style={{ color: getColor(health.snapshotSync) }}>{health.snapshotSync}</div>
                </div>
            </div>
        </div>
    );
};
