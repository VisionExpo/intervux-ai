import React from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const ExportWidget: React.FC = () => {
    const handleExport = () => {
        const events = EventCollector.getEvents();
        const data = {
            timestamp: new Date().toISOString(),
            events,
            // In a real app we'd fetch snapshot from RuntimeProvider directly, 
            // but for now we export events to prove observability works.
            snapshot: { version: "1.0", status: "mock_snapshot" }
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `intervux-diagnostics-${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <button 
            onClick={handleExport}
            style={{ 
                backgroundColor: '#0e639c', 
                color: 'white', 
                border: 'none', 
                padding: '4px 12px', 
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
            }}
        >
            Export Diagnostics
        </button>
    );
};
