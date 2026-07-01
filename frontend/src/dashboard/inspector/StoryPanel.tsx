import React, { useEffect, useState, useContext } from 'react';
import { RuntimeContext } from '../../providers/RuntimeProvider';

// Note: In production this would observe the StoryEngine through context/hooks
export const StoryPanel: React.FC = () => {
    const kernel = useContext(RuntimeContext);
    
    // For demo purposes we mock the state that would be fetched from StoryEngine.getState()
    const [engineState, setEngineState] = useState({
        scenario: "Software Engineer",
        currentChapter: "Greeting",
        currentStep: "StartPreparationCommand",
        waitingFor: "WebSocketConnected",
        elapsed: "00:00:18",
        nextStep: "TransitionWorkspaceCommand",
        isRunning: true,
        graph: [
            { id: "1", title: "Resume Uploaded", status: "completed" },
            { id: "2", title: "Resume Parsed", status: "completed" },
            { id: "3", title: "Profile Built", status: "completed" },
            { id: "4", title: "Greeting", status: "current" },
            { id: "5", title: "Question 1", status: "upcoming" },
            { id: "6", title: "Question 2", status: "upcoming" },
            { id: "7", title: "Coding", status: "upcoming" },
            { id: "8", title: "Completion", status: "upcoming" }
        ],
        commands: [
            "StartPreparation",
            "TransitionWorkspace",
            "StartAvatarSpeech"
        ]
    });

    return (
        <div className="flex flex-col h-full bg-slate-950 text-slate-300 p-4 font-mono text-xs overflow-y-auto">
            {/* Header / Engine State */}
            <div className="mb-6 border-b border-slate-800 pb-4">
                <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-100">Scenario</span>
                    <span className="text-blue-400">{engineState.scenario}</span>
                </div>
                
                <div className="flex justify-between mb-2 mt-4">
                    <span className="font-bold text-slate-400">Chapter</span>
                    <span>{engineState.currentChapter}</span>
                </div>
                <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-400">Step</span>
                    <span className="text-yellow-400">▶ {engineState.currentStep}</span>
                </div>
                <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-400">Waiting For</span>
                    <span className="text-orange-400">{engineState.waitingFor || "none"}</span>
                </div>
                
                <div className="flex justify-between mb-2 mt-4">
                    <span className="font-bold text-slate-400">Elapsed</span>
                    <span>{engineState.elapsed}</span>
                </div>
                <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-400">Next</span>
                    <span className="text-slate-500">{engineState.nextStep}</span>
                </div>
            </div>

            {/* Execution Graph */}
            <div className="mb-6">
                <span className="font-bold text-slate-100 block mb-3">Execution Graph</span>
                <div className="space-y-2">
                    {engineState.graph.map(node => (
                        <div key={node.id} className="flex items-center">
                            <span className="mr-3 w-4">
                                {node.status === 'completed' && <span className="text-green-500">✓</span>}
                                {node.status === 'current' && <span className="text-yellow-400">▶</span>}
                                {node.status === 'upcoming' && <span className="text-slate-600">○</span>}
                            </span>
                            <span className={
                                node.status === 'completed' ? 'text-slate-400' :
                                node.status === 'current' ? 'text-slate-200 font-semibold' : 'text-slate-600'
                            }>
                                {node.title}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Commands */}
            <div>
                <span className="font-bold text-slate-100 block mb-3">Commands</span>
                <div className="space-y-1 text-slate-500">
                    {engineState.commands.map((cmd, idx) => (
                        <div key={idx}>{cmd}</div>
                    ))}
                </div>
            </div>
            
            {/* Developer Controls Placeholder */}
            <div className="mt-8 border-t border-slate-800 pt-4 flex gap-2">
                <button className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-slate-300">▶ Play</button>
                <button className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-slate-300">⏸ Pause</button>
                <button className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-slate-300">⏭ Step</button>
                <button className="px-2 py-1 bg-slate-800 hover:bg-slate-700 rounded text-slate-300">↺ Restart</button>
            </div>
        </div>
    );
};
