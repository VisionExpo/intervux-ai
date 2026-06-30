import React from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const ExportWidget: React.FC = () => {
    const handleExport = () => {
        const events = EventCollector.getEvents();
        const kernel = (window as any).__runtimeKernel;
        let snapshot = {};
        if (kernel) {
            try {
                const stateModule = kernel.context.registry.getModule('StateModule');
                if (stateModule) {
                    snapshot = (stateModule as any).getSnapshot();
                }
            } catch (e) {}
        }

        const data = {
            runtime: kernel ? { status: "Active", context: "Available" } : { status: "Inactive" },
            snapshot,
            events,
            logs: events, // Currently structured logger pushes to EventCollector
            performance: {
                memory: (window.performance as any).memory || "Unavailable",
                navigation: performance.getEntriesByType("navigation")[0]
            },
            environment: {
                browser: navigator.userAgent,
                build: process.env.REACT_APP_VERSION || "1.0.0",
                commit: process.env.REACT_APP_COMMIT || "local",
                featureFlags: { developer: true } // Extracted from config in real app
            }
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
