import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';
import { LogEntry } from '../../../../core/utils/StructuredLogger';

export const EventStreamWidget: React.FC = () => {
    const [events, setEvents] = useState<LogEntry[]>([]);

    useEffect(() => {
        const unsubscribe = EventCollector.subscribe((latestEvents) => {
            setEvents(latestEvents);
        });
        return unsubscribe;
    }, []);

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178' }}>Event Stream (Latest {events.length})</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {[...events].reverse().map((ev, i) => (
                    <div key={i} style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#252526', 
                        borderRadius: '4px',
                        display: 'flex',
                        justifyContent: 'space-between'
                    }}>
                        <span style={{ color: '#569cd6' }}>[{ev.sequence}] {ev.module}</span>
                        <span style={{ color: '#4ec9b0' }}>{ev.event}</span>
                        <span style={{ color: '#dcdcaa' }}>{ev.latency_ms.toFixed(1)}ms</span>
                    </div>
                ))}
                {events.length === 0 && <div style={{ color: '#808080' }}>No events recorded yet.</div>}
            </div>
        </div>
    );
};
