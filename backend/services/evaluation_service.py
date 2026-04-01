"""
Evaluation Service - Wrapper around evaluation_engine for cleaner API.
"""

from typing import Any, Dict, Optional

from backend.core.evaluation_engine import evaluate_answer_dual
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)


class EvaluationService:
    """
    Service wrapper for answer evaluation.
    Provides a cleaner API than direct calls to evaluation_engine.
    """

    def evaluate(
        self,
        question: str,
        answer: str,
        profile: Optional[Dict[str, Any]] = None,
        lightweight: bool = False,
        temperature: float = 0.1,
        prepared_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate an interview answer.
        
        Args:
            question: The interview question asked
            answer: The candidate's transcribed answer
            profile: Candidate's resume/profile data
            lightweight: Use lightweight evaluation mode
            temperature: LLM temperature for evaluation
            prepared_context: Pre-computed evaluation context
            
        Returns:
            Evaluation results dictionary
        """
        return evaluate_answer_dual(
            question=question,
            answer=answer,
            profile=profile,
            lightweight=lightweight,
            temperature_override=temperature,
            prepared_context=prepared_context,
        )

    def evaluate_lightweight(
        self,
        question: str,
        answer: str,
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Lightweight evaluation for early assessment during streaming.
        
        Args:
            question: The interview question
            answer: The candidate's transcribed answer
            profile: Candidate's resume/profile data
            
        Returns:
            Evaluation results dictionary
        """
        return self.evaluate(
            question=question,
            answer=answer,
            profile=profile,
            lightweight=True,
            temperature=0.08,
        )

    def evaluate_full(
        self,
        question: str,
        answer: str,
        profile: Optional[Dict[str, Any]] = None,
        session_policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full evaluation with session-adaptive settings.
        
        Args:
            question: The interview question
            answer: The candidate's transcribed answer
            profile: Candidate's resume/profile data
            session_policy: Session load policy
            
        Returns:
            Evaluation results dictionary
        """
        lightweight = False
        temperature = 0.1
        
        if session_policy:
            lightweight = session_policy.get("lightweight_eval", False)
            temperature = session_policy.get("evaluation_temperature", 0.1)
        
        return self.evaluate(
            question=question,
            answer=answer,
            profile=profile,
            lightweight=lightweight,
            temperature=temperature,
        )


# Singleton instance
_evaluation_service = EvaluationService()


def get_evaluation_service() -> EvaluationService:
    """Get the evaluation service singleton."""
    return _evaluation_service


def evaluate_answer(
    question: str,
    answer: str,
    profile: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Convenience function for evaluation.
    
    Args:
        question: The interview question
        answer: The candidate's transcribed answer
        profile: Candidate's resume/profile data
        **kwargs: Additional arguments passed to evaluate_answer_dual
        
    Returns:
        Evaluation results dictionary
    """
    return _evaluation_service.evaluate(question, answer, profile, **kwargs)

