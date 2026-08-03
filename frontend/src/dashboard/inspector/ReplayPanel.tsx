import React, { useState, useContext } from 'react';
import { RuntimeContext } from '../../providers/RuntimeProvider';
import { ReplayVerifierCore } from '../../core/runtime/replay/ReplayVerifierCore';
import { DemoSessionReplay } from '../../core/runtime/replay/ReplayTypes';
import { ReplayMismatchError } from '../../core/runtime/replay/ReplayMismatch';

export const ReplayPanel: React.FC = () => {
    const kernel = useContext(RuntimeContext);
    const [status, setStatus] = useState<"idle" | "running" | "pass" | "fail">("idle");
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const [fileData, setFileData] = useState<DemoSessionReplay | null>(null);

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const json = JSON.parse(event.target?.result as string);
                setFileData(json as DemoSessionReplay);
                setStatus("idle");
                setErrorMsg(null);
            } catch (err) {
                console.error("Invalid replay file", err);
            }
        };
        reader.readAsText(file);
    };

    const runVerification = async () => {
        if (!fileData || !kernel) return;
        
        setStatus("running");
        setErrorMsg(null);
        
        // Note: For a true clean verification, we should reset the kernel state.
        // For the inspector tool, we assume the kernel is clean or we just verify on top of it.
        const verifier = new ReplayVerifierCore(kernel, fileData);

        try {
            await verifier.verify();
            setStatus("pass");
        } catch (error: any) {
            setStatus("fail");
            if (error instanceof ReplayMismatchError) {
                setErrorMsg(error.message);
            } else {
                setErrorMsg(error.message || "Unknown error occurred.");
            }
        }
    };

    return (
        <div className="flex flex-col h-full bg-slate-950 text-slate-300 p-4 font-mono text-xs overflow-y-auto">
            <h2 className="font-bold text-slate-100 mb-4 border-b border-slate-800 pb-2">Replay Inspector</h2>
            
            <div className="mb-6">
                <input 
                    type="file" 
                    accept=".json" 
                    onChange={handleFileUpload} 
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-slate-800 file:text-slate-300 hover:file:bg-slate-700"
                />
            </div>

            {fileData && (
                <div className="mb-6 space-y-2">
                    <div className="flex justify-between">
                        <span className="text-slate-400">Scenario:</span>
                        <span className="text-blue-400">{fileData.scenario}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-slate-400">Generated:</span>
                        <span className="text-slate-300">{new Date(fileData.generatedAt).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-slate-400">Ticks:</span>
                        <span className="text-slate-300">{fileData.timeline.length}</span>
                    </div>

                    <button 
                        onClick={runVerification}
                        disabled={status === "running"}
                        className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded font-bold transition-colors"
                    >
                        {status === "running" ? "Verifying..." : "Run Verification"}
                    </button>
                </div>
            )}

            {status === "pass" && (
                <div className="p-4 bg-green-900/30 border border-green-800 rounded">
                    <h3 className="text-green-400 font-bold mb-1">PASS</h3>
                    <p className="text-green-300/70">Timeline determinism perfectly matched.</p>
                </div>
            )}

            {status === "fail" && (
                <div className="p-4 bg-red-900/30 border border-red-800 rounded">
                    <h3 className="text-red-400 font-bold mb-1">MISMATCH</h3>
                    <p className="text-red-300/70">{errorMsg}</p>
                </div>
            )}
        </div>
    );
};
