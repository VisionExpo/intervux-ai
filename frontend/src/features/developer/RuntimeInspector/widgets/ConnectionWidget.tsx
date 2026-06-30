import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const ConnectionWidget: React.FC = () => {
    const [stats, setStats] = useState({
        connected: false,
        heartbeatMs: 0,
        reconnects: 0,
        packetsSent: 0,
        packetsReceived: 0,
        lastEvent: 'NONE'
    });

    useEffect(() => {
        const unsubscribe = EventCollector.subscribe((events) => {
            const kernel = (window as any).__runtimeKernel;
            if (kernel) {
                // In a full implementation, we'd pull from SocketModule
                // For now we derive from events
                const socketEvents = events.filter(e => e.module === 'SocketModule' || e.event.includes('SOCKET'));
                if (socketEvents.length > 0) {
                    const lastEvent = socketEvents[socketEvents.length - 1];
                    setStats(prev => ({
                        ...prev,
                        lastEvent: lastEvent.event,
                        connected: lastEvent.event !== 'SOCKET_DISCONNECTED',
                        packetsReceived: events.filter(e => e.event.includes('RECEIVED')).length,
                        packetsSent: events.filter(e => e.event.includes('SENT')).length,
                    }));
                }
            }
        });
        return unsubscribe;
    }, []);

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178', borderBottom: '1px solid #3c3c3c', paddingBottom: '4px' }}>Connection</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: '#808080' }}>Status</div>
                    <div style={{ color: stats.connected ? '#4ec9b0' : '#f14c4c' }}>
                        {stats.connected ? 'Connected' : 'Disconnected'}
                    </div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Heartbeat</div>
                    <div style={{ color: '#dcdcaa' }}>{stats.heartbeatMs} ms</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Reconnects</div>
                    <div style={{ color: '#dcdcaa' }}>{stats.reconnects}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Packets Sent</div>
                    <div style={{ color: '#dcdcaa' }}>{stats.packetsSent}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Packets Received</div>
                    <div style={{ color: '#dcdcaa' }}>{stats.packetsReceived}</div>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                    <div style={{ color: '#808080' }}>Last Socket Event</div>
                    <div style={{ color: '#569cd6' }}>{stats.lastEvent}</div>
                </div>
            </div>
        </div>
    );
};
