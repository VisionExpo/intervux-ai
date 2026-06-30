import React, { useEffect, useState } from 'react';
import { EventCollector } from '../../../../core/utils/EventCollector';

export const AudioWidget: React.FC = () => {
    const [audioState, setAudioState] = useState({
        microphone: 'Inactive',
        audioContext: 'Suspended',
        mediaRecorder: 'Idle',
        queueChunks: 0,
        playback: 'Idle',
        latencyMs: 0
    });

    useEffect(() => {
        const unsubscribe = EventCollector.subscribe((events) => {
            const audioEvents = events.filter(e => e.module === 'AudioManager' || e.module === 'Microphone');
            if (audioEvents.length > 0) {
                const last = audioEvents[audioEvents.length - 1];
                setAudioState(prev => ({
                    ...prev,
                    microphone: last.event.includes('RECORDING') ? 'Recording' : prev.microphone,
                    latencyMs: last.latency_ms
                }));
            }
        });
        return unsubscribe;
    }, []);

    return (
        <div>
            <h4 style={{ margin: '0 0 8px 0', color: '#ce9178', borderBottom: '1px solid #3c3c3c', paddingBottom: '4px' }}>Audio Stack</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
                <div>
                    <div style={{ color: '#808080' }}>Microphone</div>
                    <div style={{ color: audioState.microphone === 'Recording' ? '#f14c4c' : '#4ec9b0' }}>
                        {audioState.microphone}
                    </div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>AudioContext</div>
                    <div style={{ color: '#dcdcaa' }}>{audioState.audioContext}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>MediaRecorder</div>
                    <div style={{ color: '#dcdcaa' }}>{audioState.mediaRecorder}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Queue</div>
                    <div style={{ color: '#dcdcaa' }}>{audioState.queueChunks} chunks</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Playback</div>
                    <div style={{ color: '#dcdcaa' }}>{audioState.playback}</div>
                </div>
                <div>
                    <div style={{ color: '#808080' }}>Latency</div>
                    <div style={{ color: '#dcdcaa' }}>{audioState.latencyMs.toFixed(1)} ms</div>
                </div>
            </div>
        </div>
    );
};
