import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const PerformanceWidget: React.FC = () => {
    const [perf, setPerf] = useState({
        renderCount: 0,
        eventsPerSec: 0,
        avgLatencyMs: 0,
        snapshotSize: '0 KB',
        eventQueue: 0,
        heapEstimate: '0 MB',
        reactCommits: 0
    });

    useEffect(() => {
        // Track renders for the app globally if possible
        // For now, calculate stats from EventCollector
        const interval = setInterval(() => {
            const events = EventCollector.getEvents();
            if (events.length === 0) return;

            const now = new Date().getTime();
            const lastSecondEvents = events.filter(e => now - new Date(e.timestamp).getTime() < 1000);
            
            const totalLatency = events.reduce((acc, e) => acc + (e.latency_ms || 0), 0);
            const avgLatencyMs = events.length > 0 ? totalLatency / events.length : 0;

            const memory = (window.performance as any).memory;
            const heapEstimate = memory ? `${(memory.usedJSHeapSize / (1024 * 1024)).toFixed(1)} MB` : 'N/A';

            setPerf(prev => ({
                ...prev,
                eventsPerSec: lastSecondEvents.length,
                avgLatencyMs,
                heapEstimate,
                // These are placeholder heuristics until React DevTools bridge is built
                snapshotSize: `${(JSON.stringify(events).length / 1024).toFixed(1)} KB`,
                reactCommits: prev.reactCommits + Math.floor(Math.random() * 2) // mock commits for now
            }));
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178', borderBottom: '1px solid #3c3c3c', paddingBottom: '4px' }}>Performance</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: '#808080' }}>Render Count</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.renderCount}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Events/sec</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.eventsPerSec}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Avg Latency</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.avgLatencyMs.toFixed(1)} ms</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Snapshot Size</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.snapshotSize}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Event Queue</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.eventQueue}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Heap Estimate</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.heapEstimate}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>React Commits</div>
                    <div style={{ color: '#dcdcaa' }}>{perf.reactCommits}</div>
                </div>
            </div>
        </div>
    );
};
