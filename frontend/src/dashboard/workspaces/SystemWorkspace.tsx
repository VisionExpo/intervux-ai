import React, { useEffect, useState } from "react";
import { PreparationWorkspace } from "./PreparationWorkspace";
import { CompletionWorkspace } from "./CompletionWorkspace";
import { PreparationSequence, PreparationTask } from "../../core/domain/PreparationTask";

export const SystemWorkspace: React.FC = () => {
    // For now, simple local state to mock out the runtime observing
    // In production, this would subscribe to a Repository or Context
    const [subState, setSubState] = useState<"preparation" | "completion" | "waiting">("preparation");
    
    const [prepSequence, setPrepSequence] = useState<PreparationSequence>({
        overallStatus: 'active',
        tasks: [
            { id: "1", title: "Resume Parsed", state: "completed" },
            { id: "2", title: "Candidate Profile Built", state: "completed" },
            { id: "3", title: "Generating Questions", state: "running" },
            { id: "4", title: "Connecting Voice", state: "waiting" }
        ]
    });

    // We will wire this to `StoryEngine` commands later.
    // For now, it delegates to the child workspaces.

    if (subState === "preparation") {
        return <PreparationWorkspace sequence={prepSequence} />;
    }

    if (subState === "completion") {
        return <CompletionWorkspace />;
    }

    return (
        <div className="flex items-center justify-center h-full text-slate-400">
            System Workspace Idle
        </div>
    );
};
