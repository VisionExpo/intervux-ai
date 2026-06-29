import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { QuestionCard } from '../widgets/QuestionCard';

export const QuestionCardAdapter = () => {
    const { lastEvaluation, avatarText, questionIndex } = useInterviewSession();
    
    // We try to pull the current question text. If none, we fallback to avatar text or a loading state.
    const currentQuestionText = lastEvaluation?.question || avatarText || "Preparing the next interview prompt...";
    
    // Eventually difficulty might come from the backend, we default to Medium for now
    const difficulty = "Medium";

    return (
        <QuestionCard 
            title={`Question ${questionIndex > 0 ? questionIndex : 1}`}
            question={currentQuestionText}
            difficulty={difficulty}
        />
    );
};
