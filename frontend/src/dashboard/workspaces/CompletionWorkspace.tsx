import React from "react";

export const CompletionWorkspace: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center h-full w-full bg-slate-900 text-white font-sans p-8">
            <div className="max-w-md w-full text-center space-y-6">
                <div className="text-5xl text-green-400 mb-4">✓</div>
                <h1 className="text-3xl font-semibold text-slate-100">Interview Complete</h1>
                
                <div className="space-y-3 mt-8">
                    <p className="text-slate-400 animate-pulse">Analyzing Responses...</p>
                    <p className="text-slate-500">Generating Personalized Report...</p>
                    <p className="text-slate-600">Preparing Recommendations...</p>
                </div>
            </div>
        </div>
    );
};
