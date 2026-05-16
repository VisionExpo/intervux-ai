from typing import Dict, Optional
from backend.core.logging.logger import get_logger
from backend.services.llm_service import LLMService
from backend.core.llm_brain import evaluate_answer as llm_evaluate_answer

logger = get_logger(__name__)

class EvaluationService:
    """
    Orchestrates the evaluation of interview sessions.
    Handles multipass evaluation, consistency checking, and score reconciliation.
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm = llm_service or LLMService()

    def evaluate(
        self,
        question: str,
        answer: str,
        profile: Dict,
        session_policy: Optional[Dict] = None,
    ) -> Dict:
        """
        Stable adapter used by InterviewEngine.
        Delegates to the production evaluator in core.llm_brain.
        """
        policy = session_policy or {}
        lightweight = bool(policy.get("lightweight_eval", False))
        temperature = policy.get("evaluation_temperature")
        return llm_evaluate_answer(
            question=question,
            answer=answer,
            profile=profile,
            lightweight=lightweight,
            temperature_override=temperature,
        )

    def evaluate_full(
        self,
        question: str,
        answer: str,
        profile: Dict,
        session_policy: Optional[Dict] = None,
    ) -> Dict:
        """
        Backward-compatible alias.
        """
        return self.evaluate(
            question=question,
            answer=answer,
            profile=profile,
            session_policy=session_policy,
        )

    async def evaluate_session(self, session_data: Dict) -> Dict:
        """
        Performs a full evaluation of an interview session.
        """
        # Logic extracted from evaluator.py but modernized
        # 1. Analyze reasoning
        # 2. Score competencies
        # 3. Check consistency
        # 4. Reconcile final score
        
        # Placeholder for actual implementation during refactor of evaluator.py
        logger.info(f"Evaluating session {session_data.get('session_id')}")
        return {"status": "success", "score": 0.0, "feedback": "Pending refactor"}

def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
