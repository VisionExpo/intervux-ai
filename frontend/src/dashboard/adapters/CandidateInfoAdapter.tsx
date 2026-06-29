import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { CandidateInfoWidget } from '../widgets/CandidateInfoWidget';

export const CandidateInfoAdapter = () => {
    const { stage, uploadResume, audioContextRef } = useInterviewSession();

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!audioContextRef.current) {
            audioContextRef.current = new AudioContext();
        } else if (audioContextRef.current.state === "suspended") {
            audioContextRef.current.resume().catch((err) => console.warn("Failed to resume AudioContext", err));
        }

        const file = e.target.files?.[0];
        if (file) {
            await uploadResume(file);
        }
    };

    const needsResume = stage === "WAITING_RESUME" || stage === "PROCESSING_RESUME";
    const isUploadingResume = stage === "PROCESSING_RESUME";

    return (
        <CandidateInfoWidget 
            needsResume={needsResume}
            isUploadingResume={isUploadingResume}
            onUploadResume={handleFileSelect}
            candidateName="Vishal Gorule"
            role="AI/ML Engineer"
            skills={['Python', 'FastAPI', 'Docker', 'Redis']}
        />
    );
};
