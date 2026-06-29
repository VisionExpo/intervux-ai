import { useState } from 'react';
import { DashboardShell } from '../dashboard/layouts/DashboardShell';
import { CandidateInfoWidget } from '../dashboard/widgets/CandidateInfoWidget';
import { InterviewProgressWidget } from '../dashboard/widgets/InterviewProgressWidget';
import { EventTimelineWidget } from '../dashboard/widgets/EventTimelineWidget';
import { QuestionCard } from '../dashboard/widgets/QuestionCard';
import { VoiceControlPanel } from '../dashboard/widgets/VoiceControlPanel';
import { CandidateMonitor } from '../features/vision/CandidateMonitor';
import { theme } from '../design-system/tokens/theme';

export const DashboardPreview = () => {
    const [layout, setLayout] = useState<'conversation' | 'coding'>('conversation');

    const timelineEvents = [
        { id: '1', speaker: 'AI' as const, text: 'Welcome Vishal. I am your AI interviewer today. Let us get started.' },
        { id: '2', speaker: 'Candidate' as const, text: 'Hi, thanks. Im ready.' },
        { id: '3', speaker: 'AI' as const, text: 'To begin, explain the difference between a Python List and a Tuple.' }
    ];

    const TopRegion = (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
            <div style={{ fontWeight: 600, fontSize: '1.25rem' }}>Intervux <span style={{ color: theme.brand.primary }}>OS</span></div>
            <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => setLayout('conversation')} style={{ padding: '6px 12px', background: layout === 'conversation' ? theme.surface.overlay : 'transparent', color: theme.text.primary, border: '1px solid ' + theme.border.default, borderRadius: '4px', cursor: 'pointer' }}>Conversation</button>
                <button onClick={() => setLayout('coding')} style={{ padding: '6px 12px', background: layout === 'coding' ? theme.surface.overlay : 'transparent', color: theme.text.primary, border: '1px solid ' + theme.border.default, borderRadius: '4px', cursor: 'pointer' }}>Coding</button>
            </div>
            <button style={{ padding: '8px 16px', background: theme.status.error, color: 'white', border: 'none', borderRadius: '4px', fontWeight: 600, cursor: 'pointer' }}>End Interview</button>
        </div>
    );

    const LeftRegion = (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '100%', overflowY: 'auto' }}>
            <CandidateInfoWidget 
                candidateName="Vishal Gorule"
                role="AI/ML Engineer"
                skills={['Python', 'FastAPI', 'Docker', 'Redis']}
            />
            <InterviewProgressWidget 
                currentQuestion={2}
                totalQuestions={8}
                timeElapsed="18:42"
                difficulty="Medium"
            />
        </div>
    );

    const RightRegion = (
        <EventTimelineWidget events={timelineEvents} />
    );

    const BottomRegion = (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', padding: '0 24px', color: theme.text.secondary, fontSize: '0.875rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="motion-loading">🔄</span> System Operational
            </div>
        </div>
    );

    const WorkspaceRegion = (
        <div style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {layout === 'conversation' ? (
                // Conversation Layout
                <div style={{ display: 'flex', gap: '24px', flex: 1 }}>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <div style={{ flex: 1, backgroundColor: theme.surface.elevated, borderRadius: theme.radius.md, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${theme.border.default}` }}>
                            {/* Fake AI Video/Orb Placeholder */}
                            <div className="motion-speaking" style={{ width: '120px', height: '120px', borderRadius: '50%', background: `radial-gradient(circle, ${theme.interview.ai} 0%, transparent 70%)` }} />
                        </div>
                        <QuestionCard />
                    </div>
                    <div style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <CandidateMonitor />
                        <VoiceControlPanel isListening={true} />
                    </div>
                </div>
            ) : (
                // Coding Layout
                <div style={{ display: 'flex', gap: '24px', flex: 1 }}>
                    <div style={{ flex: 2, display: 'flex', flexDirection: 'column', gap: '24px' }}>
                         <div style={{ flex: 1, backgroundColor: theme.surface.elevated, borderRadius: theme.radius.md, border: `1px solid ${theme.border.default}`, padding: '16px', fontFamily: 'monospace', color: theme.text.primary }}>
                             <div style={{ color: theme.text.muted, marginBottom: '16px' }}>// Developer Workspace</div>
                             <div style={{ color: theme.brand.primary }}>def <span style={{ color: theme.text.primary }}>difference_between_list_and_tuple</span>():</div>
                             <div style={{ paddingLeft: '24px', color: theme.status.success }}>pass</div>
                         </div>
                    </div>
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
                        <QuestionCard />
                        <CandidateMonitor />
                        <VoiceControlPanel isListening={true} />
                    </div>
                </div>
            )}
        </div>
    );

    return (
        <DashboardShell 
            topRegion={TopRegion}
            leftRegion={LeftRegion}
            workspaceRegion={WorkspaceRegion}
            rightRegion={RightRegion}
            bottomRegion={BottomRegion}
        />
    );
};
