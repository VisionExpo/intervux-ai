"""
Interview Engine - Core AI logic for interview processing.

This engine handles:
- Resume parsing
- Question generation
- Audio transcription (STT)
- Answer evaluation
- Next question generation
- Report generation
"""

import asyncio
import os
import time
from functools import partial
from typing import Any, Dict, List, Optional, Tuple

from backend.core.adaptive_engine import (
    build_skill_coverage_engine,
    build_skill_map,
    generate_initial_question,
    next_question as build_next_question,
    update_topic_scores,
)
from backend.core.difficulty_engine import DifficultyCalibrationEngine
from backend.core.llm_brain import generate_final_report
from backend.core.memory_engine import (
    build_memory_context,
    seed_memory_projects,
    update_memory,
)
from backend.modules.interview.models import InterviewPhase, InterviewState, ResumeData
from backend.services.resume_parser_service import ParsedResume, parse_resume_from_b64
from backend.services.audio_buffer import AudioBuffer
from backend.services.evaluation_service import get_evaluation_service
from backend.services.stt_service import transcribe_audio_bytes
from backend.services.tts_service import synthesize_speech_with_visemes
from backend.services.viseme_service import VisemeService
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)
viseme_service = VisemeService()


class InterviewEngine:
    """
    Core AI engine for interview processing.
    
    Responsibilities:
    - Parse resume and initialize interview
    - Process audio and transcribe
    - Evaluate answers
    - Generate next questions
    - Generate final report
    """

    def __init__(self):
        self.min_questions_per_skill = int(os.getenv("MIN_QUESTIONS_PER_SKILL", "1"))
        self.difficulty_start_level = int(os.getenv("DIFFICULTY_START_LEVEL", "2"))
        self.max_questions_hard_cap = int(os.getenv("MAX_QUESTIONS_HARD_CAP", "8"))
        self.evaluation_service = get_evaluation_service()

    async def start_interview(
        self,
        state: InterviewState,
        file_name: str,
        file_bytes_b64: str,
        session_policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.info("Resume received")
        logger.info(f"Resume size: {len(file_bytes_b64)}")
        # state.transition_to(InterviewPhase.WAITING_RESUME) // REMOVED: Redundant/Incorrect
        
        logger.info("Starting resume parsing")
        resume_start = time.time()
        parsed_resume = await self._parse_resume(file_name, file_bytes_b64)
        logger.info(
            "Resume parsed",
            extra={
                "extra_data": {
                    "parser_used": parsed_resume.parser_used,
                    "skills_found": len(parsed_resume.skills),
                    "empty": parsed_resume.is_empty(),
                }
            },
        )
        extracted = parsed_resume.to_interview_profile()

        metrics.record_latency("resume_parsing", time.time() - resume_start)

        return await self.start_interview_from_profile(
            state=state,
            profile_data=extracted,
            session_policy=session_policy,
        )

    async def start_interview_from_profile(
        self,
        state: InterviewState,
        profile_data: Dict[str, Any],
        session_policy: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            state.profile = ResumeData(**(profile_data or {}))
        except Exception:
            logger.exception("Failed to build ResumeData from profile data")
            state.profile = ResumeData()

        logger.info("Generating first question")
        question_start = time.time()
        state.target_question_count = int(session_policy.get("question_count", 2))
        state.skill_map = build_skill_map(state.profile.model_dump())
        state.skill_coverage = build_skill_coverage_engine(state.profile.model_dump())
        state.topic_scores = {}
        state.difficulty_engine = DifficultyCalibrationEngine(
            start_level=self.difficulty_start_level
        )
        state.current_difficulty = state.difficulty_engine.level
        state.skill_max_difficulty = {}
        seed_memory_projects(state.memory, state.profile.model_dump())
        
        initial_memory_context = build_memory_context(state.memory)
        (
            first_question,
            first_skill,
            first_topic,
            first_strategy,
            first_difficulty,
            first_concept,
            first_concept_difficulty,
        ) = await self._generate_initial_question(
            skill_map=state.skill_map,
            coverage_engine=state.skill_coverage,
            question_temperature=session_policy.get("question_temperature", 0.7),
            memory_context=initial_memory_context,
            start_difficulty=state.current_difficulty,
        )
        
        state.questions = [first_question]
        state.question_skills = [first_skill]
        state.question_strategies = [first_strategy]
        state.topics = [first_topic]
        state.concepts = [first_concept]
        state.concept_difficulties = [first_concept_difficulty]
        state.current_difficulty = first_difficulty
        state.current_index = 0
        
        metrics.record_latency("question_generation", time.time() - question_start)
        state.transition_to(InterviewPhase.QUESTION)
        
        return {
            "type": "question",
            "text": first_question,
            "question_index": 1,
            "total_questions": state.target_question_count,
        }

    async def process_audio(
        self,
        state: InterviewState,
        audio_bytes: bytes,
        question: str,
        profile: dict,
        session_policy: Dict[str, Any],
        draft_transcript: str = "",
        early_eval_task: Any = None,
    ) -> Dict[str, Any]:
        stt_start = time.time()
        if audio_bytes:
            transcript = await self._transcribe_audio(
                audio_bytes,
                self._detect_audio_suffix(audio_bytes)
            )
        else:
            transcript = ""
            
        stt_duration = time.time() - stt_start
        metrics.record_latency("stt", stt_duration)
        if not transcript:
            transcript = "(No transcript captured)"
            
        return {
            "audio_bytes": audio_bytes,
            "transcript": transcript,
            "stt_duration": stt_duration,
            "speech_duration": self._estimate_speech_duration(audio_bytes),
        }

    async def evaluate_answer(
        self,
        state: InterviewState,
        audio_bytes: bytes,
        transcript: str,
        question: str,
        session_policy: Dict[str, Any],
        eval_context_cache: Dict[int, dict],
        draft_transcript: str = "",
        early_eval_task: Any = None,
    ) -> Dict[str, Any]:
        state.transition_to(InterviewPhase.PROCESSING)
        
        current_index = state.current_index
        skill = state.question_skills[current_index] if current_index < len(state.question_skills) else "Machine Learning"
        strategy = state.question_strategies[current_index] if current_index < len(state.question_strategies) else "follow_up"
        topic = state.topics[current_index] if current_index < len(state.topics) else "general"
        concept = state.concepts[current_index] if current_index < len(state.concepts) else topic
        concept_difficulty = state.concept_difficulties[current_index] if current_index < len(state.concept_difficulties) else state.current_difficulty
        
        eval_start = time.time()
        evaluation = await self._evaluate(
            question=question,
            answer=transcript,
            profile=state.profile.model_dump(),
            session_policy=session_policy,
            current_index=current_index,
            eval_context_cache=eval_context_cache,
            draft_transcript=draft_transcript,
            early_eval_task=early_eval_task,
        )
        eval_duration = time.time() - eval_start
        metrics.record_latency("evaluation", eval_duration)
        
        # Anomaly Detection Optimization
        current_score = float(evaluation.get("final", {}).get("score", 0.0))
        historical_scores = [float(ans.get("evaluation", {}).get("final", {}).get("score", 0.0)) for ans in state.answers[-3:]]
        
        if historical_scores:
            rolling_avg = sum(historical_scores) / len(historical_scores)
            if abs(current_score - rolling_avg) > 3.0:
                logger.warning(f"Anomaly Detected! Score {current_score} deviates from rolling average {rolling_avg} by >3 points.")
                evaluation.setdefault("meta", {})["anomaly_flagged"] = True
        
        update_topic_scores(state.topic_scores, topic, evaluation)
        update_memory(
            state.memory,
            question=question,
            answer=transcript,
            evaluation=evaluation,
            topic=topic,
        )
        
        state.answers.append({
            "question": question,
            "skill": skill,
            "strategy": strategy,
            "topic": topic,
            "concept": concept,
            "concept_difficulty": concept_difficulty,
            "answer": transcript,
            "evaluation": evaluation,
        })
        
        if state.skill_coverage is not None:
            state.skill_coverage.update(skill)
        state.skill_max_difficulty[skill] = max(
            state.skill_max_difficulty.get(skill, 1),
            int(concept_difficulty),
        )
        
        state.current_index += 1
        
        return {
            "type": "evaluation",
            "data": {
                "question_index": current_index + 1,
                "question": question,
                "skill": skill,
                "strategy": strategy,
                "topic": topic,
                "concept": concept,
                "concept_difficulty": concept_difficulty,
                "transcript": transcript,
                "evaluation": evaluation,
            },
        }

    async def generate_next_question(
        self,
        state: InterviewState,
        last_evaluation: dict,
        session_policy: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if not self._should_continue(state):
            return None
            
        state.transition_to(InterviewPhase.NEXT_QUESTION)
        
        last_answer = state.answers[-1] if state.answers else {}
        topic = last_answer.get("topic", "general")
        skill = last_answer.get("skill", "Machine Learning")
        question = last_answer.get("question", "")
        
        score_value = sum(last_evaluation.get("scores", {}).values()) / max(1, len(last_evaluation.get("scores", {})))
        confidence_value = float(last_evaluation.get("confidence_score", 0.7) or 0.7)
        
        if state.difficulty_engine is not None:
            state.current_difficulty = state.difficulty_engine.update(
                score_value, confidence_value
            )
        
        memory_context = build_memory_context(state.memory)
        current_concept = state.concepts[-1] if state.concepts else ""

        (
            generated_question,
            next_skill,
            next_topic,
            next_strategy,
            next_difficulty,
            next_concept,
            next_concept_difficulty,
        ) = await self._generate_next_question(
            score=score_value,
            confidence=confidence_value,
            topic_scores=state.topic_scores,
            skill_map=state.skill_map,
            coverage_engine=state.skill_coverage,
            difficulty=state.current_difficulty,
            last_topic=topic,
            last_skill=skill,
            last_question=question,
            evaluation_summary=str(last_evaluation.get("summary", "") or ""),
            question_temperature=session_policy.get("question_temperature", 0.7),
            memory_context=memory_context,
            current_concept=current_concept,
        )
        
        state.questions.append(generated_question)
        state.question_skills.append(next_skill)
        state.question_strategies.append(next_strategy)
        state.topics.append(next_topic)
        state.concepts.append(next_concept)
        state.concept_difficulties.append(next_concept_difficulty)
        state.current_difficulty = next_difficulty
        
        state.transition_to(InterviewPhase.QUESTION)
        
        return {
            "type": "next_question",
            "text": generated_question,
            "question_index": state.current_index + 1,
            "total_questions": max(state.target_question_count, len(state.questions)),
        }

    async def complete_interview(
        self,
        state: InterviewState,
    ) -> Dict[str, Any]:
        state.transition_to(InterviewPhase.COMPLETE)
        report_start = time.time()
        report = await self._generate_report(
            profile=state.profile.model_dump(),
            answers=state.answers,
        )
        if isinstance(report, dict):
            report["skill_performance"] = self._build_skill_performance_summary(state)
            
        metrics.record_latency("final_report", time.time() - report_start)
        metrics.record_interview_completed()
        state.final_report = report
        
        return {
            "type": "interview_complete",
            "report": report,
        }

    def _should_continue(self, state: InterviewState) -> bool:
        if state.current_index >= self.max_questions_hard_cap:
            return False
        under_target = state.current_index < state.target_question_count
        if state.skill_coverage is None:
            return under_target
        coverage_met = state.skill_coverage.meets_minimum(self.min_questions_per_skill)
        return under_target or (not coverage_met)

    # ==================== Private Helper Methods ====================

    async def _parse_resume(self, file_name: str, file_bytes_b64: str) -> ParsedResume:
        try:
            return await asyncio.to_thread(parse_resume_from_b64, file_name, file_bytes_b64)
        except Exception:
            logger.exception("Resume parsing failed")
            return ParsedResume(parser_used="failed")

    async def _generate_initial_question(
        self,
        skill_map: dict,
        coverage_engine: Any,
        question_temperature: float,
        memory_context: str,
        start_difficulty: int,
    ) -> Tuple[str, str, str, str, int, str, int]:
        return await asyncio.to_thread(
            partial(
                generate_initial_question,
                skill_map=skill_map,
                coverage_engine=coverage_engine,
                question_temperature=question_temperature,
                memory_context=memory_context,
                start_difficulty=start_difficulty,
            )
        )

    async def _generate_next_question(
        self,
        score: float,
        confidence: float,
        topic_scores: dict,
        skill_map: dict,
        coverage_engine: Any,
        difficulty: int,
        last_topic: str,
        last_skill: str,
        last_question: str,
        evaluation_summary: str,
        question_temperature: float,
        memory_context: str,
        current_concept: str,
    ) -> Tuple[str, str, str, str, int, str, int]:
        return await asyncio.to_thread(
            partial(
                build_next_question,
                score=score,
                confidence=confidence,
                topic_scores=topic_scores,
                skill_map=skill_map,
                coverage_engine=coverage_engine,
                difficulty=difficulty,
                last_topic=last_topic,
                last_skill=last_skill,
                last_question=last_question,
                evaluation_summary=evaluation_summary,
                question_temperature=question_temperature,
                memory_context=memory_context,
                current_concept=current_concept,
            )
        )

    async def _transcribe_audio(self, audio_bytes: bytes, suffix: str) -> str:
        return await asyncio.to_thread(
            partial(
                transcribe_audio_bytes,
                audio_bytes=audio_bytes,
                suffix=suffix,
            )
        )

    async def _evaluate(
        self,
        question: str,
        answer: str,
        profile: dict,
        session_policy: Dict[str, Any],
        current_index: int,
        eval_context_cache: Dict[int, dict],
        draft_transcript: str = "",
        early_eval_task: Any = None,
    ) -> dict:
        return await asyncio.to_thread(
            partial(
                self.evaluation_service.evaluate,
                question=question,
                answer=answer,
                profile=profile,
                session_policy=session_policy,
            )
        )

    async def _generate_report(self, profile: dict, answers: list) -> dict:
        return await asyncio.to_thread(
            partial(
                generate_final_report,
                profile=profile,
                answers=answers,
            )
        )

    @staticmethod
    def _build_skill_performance_summary(state: InterviewState) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for answer in state.answers:
            skill = answer.get("skill")
            if not isinstance(skill, str) or not skill.strip():
                skill = "Unknown"
                
            scores = answer.get("evaluation", {}).get("scores", {})
            values = []
            if isinstance(scores, dict):
                for value in scores.values():
                    try:
                        values.append(float(value))
                    except Exception:
                        continue
                        
            avg_score = sum(values) / len(values) if values else 0.0
            bucket = summary.setdefault(skill, {"_sum": 0.0, "_count": 0.0, "max_difficulty_reached": 1.0})
            bucket["_sum"] += avg_score
            bucket["_count"] += 1.0
            bucket["max_difficulty_reached"] = max(
                bucket["max_difficulty_reached"],
                float(state.skill_max_difficulty.get(skill, 1)),
            )

        result: Dict[str, Dict[str, float]] = {}
        for skill, item in summary.items():
            count = item["_count"] or 1.0
            result[skill] = {
                "score": round(item["_sum"] / count, 2),
                "max_difficulty_reached": round(item["max_difficulty_reached"], 0),
            }
        return result

    @staticmethod
    def _detect_audio_suffix(audio_bytes: bytes) -> str:
        if audio_bytes.startswith(b"RIFF"):
            return ".wav"
        if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            return ".webm"
        if audio_bytes.startswith(b"ID3"):
            return ".mp3"
        return ".wav"

    @staticmethod
    def _estimate_speech_duration(audio_bytes: bytes) -> float:
        if len(audio_bytes) < 44:
            return 0.0
        return len(audio_bytes) / 32000
