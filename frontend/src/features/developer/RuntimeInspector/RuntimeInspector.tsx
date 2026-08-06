import React, { useState, useEffect } from 'react';
import { isCapabilityEnabled } from '../../../core/config/PlatformCapabilities';
import { EventStreamWidget } from './widgets/EventStreamWidget';
import { ExportWidget } from './widgets/ExportWidget';
import { RuntimeWidget } from './widgets/RuntimeWidget';
import { ConnectionWidget } from './widgets/ConnectionWidget';
import { AudioWidget } from './widgets/AudioWidget';
import { PerformanceWidget } from './widgets/PerformanceWidget';
import { DiagnosticsWidget } from './widgets/DiagnosticsWidget';
import { ProjectionWidget } from './widgets/ProjectionWidget';

export const RuntimeInspector: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        if (!isCapabilityEnabled('developer')) return;

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'd') {
                e.preventDefault();
                setIsOpen(prev => !prev);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    if (!isOpen || !isCapabilityEnabled('developer')) return null;

    return (
        <div style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            height: '40vh',
            backgroundColor: '#1e1e1e',
            color: '#d4d4d4',
            zIndex: 9999,
            borderTop: '2px solid #007acc',
            display: 'flex',
            flexDirection: 'column',
            fontFamily: 'monospace',
            fontSize: '12px'
        }}>
            <div style={{
                padding: '8px 16px',
                backgroundColor: '#2d2d2d',
                borderBottom: '1px solid #3c3c3c',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <h3 style={{ margin: 0, color: '#4fc1ff' }}>Runtime Inspector</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <ExportWidget />
                    <button 
                        onClick={() => setIsOpen(false)}
                        style={{ background: 'transparent', border: 'none', color: '#d4d4d4', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        ✕ Close
                    </button>
                </div>
            </div>
            
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
                <div style={{ flex: 1, borderRight: '1px solid #3c3c3c', overflowY: 'auto', padding: '16px' }}>
                    <EventStreamWidget />
                </div>
                <div style={{ width: '400px', padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <RuntimeWidget />
                    <ProjectionWidget />
                    <ConnectionWidget />
                    <AudioWidget />
                    <PerformanceWidget />
                    <DiagnosticsWidget />
                </div>
            </div>
        </div>
    );
};
