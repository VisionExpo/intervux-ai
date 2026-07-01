import React from "react";
import { PreparationSequence, PreparationTask } from "../../core/domain/PreparationTask";

interface PreparationWorkspaceProps {
    sequence: PreparationSequence;
}

export const PreparationWorkspace: React.FC<PreparationWorkspaceProps> = ({ sequence }) => {
    return (
        <div className="flex flex-col items-center justify-center h-full w-full bg-slate-900 text-white font-sans p-8">
            <div className="max-w-md w-full">
                <h1 className="text-3xl font-semibold mb-8 text-center text-slate-100">Preparing Interview</h1>
                
                <div className="space-y-4">
                    {sequence.tasks.map(task => (
                        <div key={task.id} className="flex items-center p-4 bg-slate-800 rounded-lg shadow-sm border border-slate-700">
                            <div className="mr-4">
                                {task.state === 'completed' && <span className="text-green-400">✓</span>}
                                {task.state === 'running' && <span className="text-blue-400 animate-pulse">●</span>}
                                {task.state === 'failed' && <span className="text-red-400">❌</span>}
                                {task.state === 'waiting' && <span className="text-slate-500">○</span>}
                            </div>
                            <div className={`text-lg transition-colors ${
                                task.state === 'running' ? 'text-blue-100' :
                                task.state === 'waiting' ? 'text-slate-500' :
                                task.state === 'failed' ? 'text-red-300' : 'text-slate-300'
                            }`}>
                                {task.title}
                            </div>
                        </div>
                    ))}
                </div>

                {sequence.overallStatus === 'failed' && (
                    <div className="mt-8 text-center">
                        <button className="px-6 py-2 bg-red-600 hover:bg-red-500 text-white rounded-md transition-colors">
                            Retry
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
