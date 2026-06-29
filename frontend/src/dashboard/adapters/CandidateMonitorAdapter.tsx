import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { CandidateCamera } from '../../components/interview';
import { CandidateMonitor } from '../../features/vision/CandidateMonitor';

export const CandidateMonitorAdapter = () => {
    const { mediaStream, isSpeaking, stage } = useInterviewSession();
    const isListening = stage === "LISTENING";
    return (
        <CandidateMonitor>
            <CandidateCamera 
              isEnabled={true} 
              stream={mediaStream} 
              isListening={isListening} 
              isSpeaking={isSpeaking} 
            />
        </CandidateMonitor>
    );
};
