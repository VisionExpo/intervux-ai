import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { InterviewProgressWidget } from '../widgets/InterviewProgressWidget';

export const InterviewProgressAdapter = () => {
    const { questionIndex, totalQuestions } = useInterviewSession();

    return (
        <InterviewProgressWidget 
            currentQuestion={questionIndex > 0 ? questionIndex : 1}
            totalQuestions={totalQuestions > 0 ? totalQuestions : 5}
            timeElapsed="--"
            difficulty="Medium"
        />
    );
};
