import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';
import { LogEntry } from '../../../../core/utils/StructuredLogger';

export const EventStreamWidget: React.FC = () => {
    const [events, setEvents] = useState<LogEntry[]>([]);
    const [filter, setFilter] = useState('All');
    const [search, setSearch] = useState('');
    const [selectedEvent, setSelectedEvent] = useState<LogEntry | null>(null);
    const [scrubIndex, setScrubIndex] = useState<number | null>(null);

    useEffect(() => {
        const unsubscribe = EventCollector.subscribe((latestEvents) => {
            setEvents(latestEvents);
            if (scrubIndex === null && latestEvents.length > 0) {
                // Autoscroll logic could go here
            }
        });
        return unsubscribe;
    }, [scrubIndex]);

    const filters = ['All', 'Socket', 'Audio', 'Interview', 'Runtime', 'Vision', 'Telemetry'];

    const filteredEvents = events.filter(e => {
        if (filter !== 'All' && !e.module.includes(filter) && !e.event.includes(filter.toUpperCase())) return false;
        if (search && !e.event.toLowerCase().includes(search.toLowerCase()) && !e.module.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    const displayEvents = scrubIndex !== null ? filteredEvents.slice(0, scrubIndex) : filteredEvents;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h4 style={{ margin: 0, color: '#ce9178' }}>Event Stream ({displayEvents.length})</h4>
                <input 
                    type="text" 
                    placeholder="Search..." 
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    style={{ background: '#3c3c3c', border: 'none', color: '#fff', padding: '2px 8px', borderRadius: '4px' }}
                />
            </div>
            
            <div style={{ display: 'flex', gap: '4px', marginBottom: '8px', flexWrap: 'wrap' }}>
                {filters.map(f => (
                    <button 
                        key={f}
                        onClick={() => setFilter(f)}
                        style={{ 
                            background: filter === f ? '#0e639c' : '#3c3c3c', 
                            color: '#fff', border: 'none', padding: '2px 8px', borderRadius: '4px', cursor: 'pointer' 
                        }}
                    >
                        {f}
                    </button>
                ))}
            </div>

            {events.length > 0 && (
                <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: '#808080' }}>Timeline:</span>
                    <input 
                        type="range" 
                        min={1} 
                        max={filteredEvents.length} 
                        value={scrubIndex ?? filteredEvents.length}
                        onChange={e => setScrubIndex(parseInt(e.target.value))}
                        style={{ flex: 1 }}
                    />
                    <button 
                        onClick={() => setScrubIndex(null)}
                        style={{ background: 'transparent', color: '#4fc1ff', border: '1px solid #4fc1ff', borderRadius: '4px', cursor: 'pointer' }}
                    >
                        Live
                    </button>
                </div>
            )}

            <div style={{ display: 'flex', flex: 1, gap: '16px', overflow: 'hidden' }}>
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {[...displayEvents].reverse().map((ev, i) => (
                        <div 
                            key={ev.sequence} 
                            onClick={() => setSelectedEvent(ev)}
                            style={{ 
                                padding: '4px 8px', 
                                backgroundColor: selectedEvent?.sequence === ev.sequence ? '#37373d' : '#252526', 
                                borderRadius: '4px',
                                display: 'flex',
                                justifyContent: 'space-between',
                                cursor: 'pointer',
                                borderLeft: selectedEvent?.sequence === ev.sequence ? '2px solid #007acc' : '2px solid transparent'
                            }}
                        >
                            <span style={{ color: '#569cd6' }}>[{ev.sequence}] {ev.module}</span>
                            <span style={{ color: '#4ec9b0' }}>{ev.event}</span>
                            <span style={{ color: '#dcdcaa' }}>{ev.latency_ms.toFixed(1)}ms</span>
                        </div>
                    ))}
                    {displayEvents.length === 0 && <div style={{ color: '#808080' }}>No events match filters.</div>}
                </div>
                
                {selectedEvent && (
                    <div style={{ width: '300px', backgroundColor: '#252526', padding: '8px', borderRadius: '4px', overflowY: 'auto' }}>
                        <h4 style={{ margin: '0 0 8px 0', color: '#4fc1ff' }}>Event Details</h4>
                        <div style={{ color: '#808080' }}>Sequence: <span style={{ color: '#dcdcaa' }}>#{selectedEvent.sequence}</span></div>
                        <div style={{ color: '#808080' }}>Module: <span style={{ color: '#569cd6' }}>{selectedEvent.module}</span></div>
                        <div style={{ color: '#808080' }}>Event: <span style={{ color: '#4ec9b0' }}>{selectedEvent.event}</span></div>
                        <div style={{ color: '#808080' }}>Latency: <span style={{ color: '#dcdcaa' }}>{selectedEvent.latency_ms}ms</span></div>
                        
                        <h5 style={{ margin: '8px 0 4px 0', color: '#ce9178' }}>Payload</h5>
                        <pre style={{ margin: 0, padding: '4px', backgroundColor: '#1e1e1e', fontSize: '10px', overflowX: 'auto' }}>
                            {JSON.stringify(selectedEvent.metadata?.payload || {}, null, 2)}
                        </pre>
                        
                        <h5 style={{ margin: '8px 0 4px 0', color: '#ce9178' }}>Metadata</h5>
                        <pre style={{ margin: 0, padding: '4px', backgroundColor: '#1e1e1e', fontSize: '10px', overflowX: 'auto' }}>
                            {JSON.stringify(selectedEvent.metadata || {}, null, 2)}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
};
