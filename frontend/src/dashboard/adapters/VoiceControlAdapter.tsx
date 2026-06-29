import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { VoiceControlPanel } from '../widgets/VoiceControlPanel';

export const VoiceControlAdapter = () => {
    const { stage, endAnswer } = useInterviewSession();
    const isListening = stage === "LISTENING";

    return (
        <VoiceControlPanel 
            isListening={isListening}
            onDoneSpeaking={endAnswer}
        />
    );
};
