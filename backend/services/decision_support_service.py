"""
Decision Support Service for Recruiter Recommendations.

This service uses LLM to generate:
- Candidate performance summaries
- Skill assessments
- Interview recommendations (move to next round, hold, etc.)

Example output:
    Candidate Summary
    - Strong Python fundamentals
    - Moderate system design knowledge
    - Communication clarity above average
    
    Recommendation: Move to next round
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from backend.core.llm_brain import run_safe_json_task, BaseEvaluationModel
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# Prompt Templates
# =========================================================

CANDIDATE_SUMMARY_PROMPT = """
You are a technical recruiter assistant. Analyze the candidate's interview performance and provide a summary.

Interview Answers and Scores:
{answers_summary}

Generate a JSON response with the following structure:
{{
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses or areas for improvement"],
    "communication_assessment": "excellent/good/moderate/below_average",
    "technical_proficiency": {{
        "skill_name": "excellent/good/moderate/below_average"
    }},
    "overall_impression": "brief summary"
}}
""".strip()

RECOMMENDATION_PROMPT = """
Based on the candidate's interview performance, provide a hiring recommendation.

Candidate Summary:
{candidate_summary}

Interview Scores:
- Overall Score: {overall_score}
- Technical Score: {technical_score}
- Behavioral Score: {behavioral_score}
- Reasoning Score: {reasoning_score}

Generate a JSON response with the following structure:
{{
    "recommendation": "strong_yes/yes/hold/no",
    "confidence": 0.0-1.0,
    "rationale": "brief explanation",
    "next_steps": ["suggested next steps"],
    "role_fit": "senior/junior/mid/entry"
}}
""".strip()


class CandidateSummaryModel(BaseEvaluationModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    communication_assessment: str = "moderate"
    technical_proficiency: Dict[str, str] = Field(default_factory=dict)
    overall_impression: str = "Summary generation failed"

    @field_validator("strengths", "weaknesses", mode="before")
    @classmethod
    def normalize_list(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split("\n") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


class RecommendationModel(BaseEvaluationModel):
    recommendation: str = "hold"
    confidence: float = 0.5
    rationale: str = ""
    next_steps: List[str] = Field(default_factory=list)
    role_fit: str = "entry"

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        try:
            val = float(v)
        except (ValueError, TypeError):
            val = 0.5
        return max(0.0, min(1.0, val))

    @field_validator("next_steps", mode="before")
    @classmethod
    def normalize_steps(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split("\n") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


# =========================================================
# Decision Support Service
# =========================================================

class DecisionSupportService:
    """
    Service for generating candidate decision support.
    
    Example usage:
        decision_support = DecisionSupportService()
        
        summary = decision_support.generate_candidate_summary(
            answers=[
                {"question": "Python", "answer": "...", "score": 8.5},
                {"question": "System Design", "answer": "...", "score": 6.0},
            ]
        )
        
        recommendation = decision_support.get_recommendation(
            summary=summary,
            overall_score=7.5,
            technical_score=7.2,
            behavioral_score=8.0,
            reasoning_score=7.0,
        )
    """
    
    def generate_candidate_summary(
        self,
        answers: List[Dict[str, Any]],
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a summary of candidate performance.
        
        Args:
            answers: List of answer dictionaries with question, answer, score
            profile: Optional candidate profile information
            
        Returns:
            Dictionary containing candidate summary
        """
        # Build answers summary text
        answers_summary = []
        for i, answer in enumerate(answers, 1):
            question = answer.get("question", "Unknown")
            answer_text = answer.get("answer", "")[:500]  # Limit length
            score = answer.get("score", answer.get("evaluation", {}).get("final", {}).get("score", 0))
            scores = answer.get("evaluation", {}).get("scores", {})
            
            answers_summary.append(
                f"Q{i}: {question}\n"
                f"Answer: {answer_text[:200]}...\n"
                f"Score: {score}/10\n"
                f"Details: {scores}"
            )
        
        answers_text = "\n\n".join(answers_summary)
        
        # Add profile info if available
        if profile:
            skills = profile.get("skills", [])
            if skills:
                answers_text += f"\n\nCandidate Skills: {', '.join(skills)}"
        
        # Generate summary using LLM
        prompt = CANDIDATE_SUMMARY_PROMPT.format(answers_summary=answers_text)
        result = run_safe_json_task(
            prompt,
            CandidateSummaryModel,
            temperature=0.3,
            fallback_factory=CandidateSummaryModel
        )
        return result.model_dump()
    
    def get_recommendation(
        self,
        summary: Dict[str, Any],
        overall_score: float,
        technical_score: float,
        behavioral_score: float,
        reasoning_score: float,
    ) -> Dict[str, Any]:
        """
        Get hiring recommendation based on scores and summary.
        
        Args:
            summary: Candidate summary from generate_candidate_summary
            overall_score: Overall interview score (0-10)
            technical_score: Technical score (0-10)
            behavioral_score: Behavioral score (0-10)
            reasoning_score: Reasoning score (0-10)
            
        Returns:
            Dictionary containing recommendation
        """
        # Build summary text for prompt
        summary_text = f"Strengths: {', '.join(summary.get('strengths', []))}\n"
        summary_text += f"Weaknesses: {', '.join(summary.get('weaknesses', []))}\n"
        summary_text += f"Communication: {summary.get('communication_assessment', 'unknown')}\n"
        summary_text += f"Overall Impression: {summary.get('overall_impression', '')}"
        
        prompt = RECOMMENDATION_PROMPT.format(
            candidate_summary=summary_text,
            overall_score=overall_score,
            technical_score=technical_score,
            behavioral_score=behavioral_score,
            reasoning_score=reasoning_score,
        )
        result = run_safe_json_task(
            prompt,
            RecommendationModel,
            temperature=0.2,
            fallback_factory=lambda: RecommendationModel.model_validate(
                self._default_recommendation(overall_score)
            )
        )
        return result.model_dump()
    
    def _default_summary(self) -> Dict[str, Any]:
        """Return default summary when LLM fails."""
        return {
            "strengths": ["Unable to analyze"],
            "weaknesses": [],
            "communication_assessment": "unknown",
            "technical_proficiency": {},
            "overall_impression": "Summary generation failed",
        }
    
    def _default_recommendation(self, score: float) -> Dict[str, Any]:
        """Return default recommendation based on score."""
        if score >= 8.0:
            return {
                "recommendation": "strong_yes",
                "confidence": 0.8,
                "rationale": "High overall score",
                "next_steps": ["Proceed to next round"],
                "role_fit": "senior",
            }
        elif score >= 6.5:
            return {
                "recommendation": "yes",
                "confidence": 0.7,
                "rationale": "Good overall performance",
                "next_steps": ["Consider for next round"],
                "role_fit": "mid",
            }
        elif score >= 5.0:
            return {
                "recommendation": "hold",
                "confidence": 0.6,
                "rationale": "Average performance",
                "next_steps": ["Request additional evaluation"],
                "role_fit": "junior",
            }
        else:
            return {
                "recommendation": "no",
                "confidence": 0.8,
                "rationale": "Below threshold performance",
                "next_steps": ["Thank candidate for their time"],
                "role_fit": "entry",
            }
    
    def generate_full_report(
        self,
        answers: List[Dict[str, Any]],
        profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a full decision support report.
        
        Args:
            answers: List of answer dictionaries
            profile: Optional candidate profile
            
        Returns:
            Complete report with summary and recommendation
        """
        # Calculate aggregate scores
        overall_score = 0.0
        technical_score = 0.0
        behavioral_score = 0.0
        reasoning_score = 0.0
        count = 0
        
        for answer in answers:
            scores = answer.get("evaluation", {}).get("scores", {})
            if scores:
                overall_score += scores.get("Overall", scores.get("Technical", 0))
                technical_score += scores.get("Technical", 0)
                behavioral_score += scores.get("Behavioral", 0)
                reasoning_score += scores.get("Reasoning", scores.get("ConceptConsistency", 0))
                count += 1
        
        if count > 0:
            overall_score /= count
            technical_score /= count
            behavioral_score /= count
            reasoning_score /= count
        
        # Generate summary
        summary = self.generate_candidate_summary(answers, profile)
        
        # Get recommendation
        recommendation = self.get_recommendation(
            summary=summary,
            overall_score=overall_score,
            technical_score=technical_score,
            behavioral_score=behavioral_score,
            reasoning_score=reasoning_score,
        )
        
        return {
            "candidate_summary": summary,
            "recommendation": recommendation,
            "scores": {
                "overall": round(overall_score, 2),
                "technical": round(technical_score, 2),
                "behavioral": round(behavioral_score, 2),
                "reasoning": round(reasoning_score, 2),
            },
            "answers_count": count,
        }


# Singleton instance
decision_support_service = DecisionSupportService()


# =========================================================
# Convenience Functions
# =========================================================

def generate_candidate_summary(
    answers: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function to generate candidate summary."""
    return decision_support_service.generate_candidate_summary(answers, profile)


def get_recommendation(
    summary: Dict[str, Any],
    overall_score: float,
    technical_score: float,
    behavioral_score: float,
    reasoning_score: float,
) -> Dict[str, Any]:
    """Convenience function to get recommendation."""
    return decision_support_service.get_recommendation(
        summary, overall_score, technical_score, behavioral_score, reasoning_score
    )


def generate_full_report(
    answers: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Convenience function to generate full decision support report."""
    return decision_support_service.generate_full_report(answers, profile)

