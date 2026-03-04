import json
import os
import threading
import time
import urllib.error
import urllib.request
from statistics import mean
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from google import genai

from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

load_dotenv()

logger = get_logger(__name__)


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
LLM_FALLBACK_PROVIDER = os.getenv("LLM_FALLBACK_PROVIDER", "qwen").strip().lower()
LLM_AUTO_FALLBACK = _env_flag("LLM_AUTO_FALLBACK", True)
LLM_FALLBACK_ON_ANY_ERROR = _env_flag("LLM_FALLBACK_ON_ANY_ERROR", False)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_CLIENT = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:7b-instruct")
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
LOCAL_LLM_TIMEOUT_S = int(os.getenv("LOCAL_LLM_TIMEOUT_S", "120"))
LLM_CIRCUIT_BREAKER_ENABLED = _env_flag("LLM_CIRCUIT_BREAKER_ENABLED", True)
LLM_CB_FAILURE_THRESHOLD = int(os.getenv("LLM_CB_FAILURE_THRESHOLD", "3"))
LLM_CB_SLOW_THRESHOLD_S = float(os.getenv("LLM_CB_SLOW_THRESHOLD_S", "12"))
LLM_CB_SLOW_STRIKES_THRESHOLD = int(os.getenv("LLM_CB_SLOW_STRIKES_THRESHOLD", "3"))
LLM_CB_OPEN_SECONDS = int(os.getenv("LLM_CB_OPEN_SECONDS", "60"))
EVAL_MULTI_PASS = _env_flag("EVAL_MULTI_PASS", True)
EVAL_SELF_CONSISTENCY = _env_flag("EVAL_SELF_CONSISTENCY", True)

RUBRIC_FULL = [
    "Technical Accuracy",
    "Clarity of Explanation",
    "Depth of Understanding",
    "Confidence & Communication",
]
RUBRIC_LITE = ["Technical Accuracy", "Clarity of Explanation"]
RUBRIC_JSON_FULL = json.dumps(RUBRIC_FULL, separators=(",", ":"))
RUBRIC_JSON_LITE = json.dumps(RUBRIC_LITE, separators=(",", ":"))

QUESTION_PROMPT_TEMPLATE = """
You are an AI interviewer.
Return ONLY JSON list[str] with exactly {num_questions} concise technical questions.
No markdown, no extra text.
Profile: {profile_json}
""".strip()

NEXT_QUESTION_PROMPT_TEMPLATE = """
You are an AI interviewer.
Generate ONE concise technical interview question.
Return ONLY JSON:
{{"question":"...","skill":"..."}}
No markdown, no extra text.
Topic: {topic}
Concept: {concept}
Difficulty: {difficulty}
Strategy: {strategy}
Preferred Skill: {preferred_skill}
Allowed Skills: {allowed_skills_json}
Previous Question: {previous_question}
Evaluation Summary: {evaluation_summary}
Memory Context:
{memory_context}
Generate a question that can reference earlier candidate statements when relevant.
""".strip()

EVAL_PROMPT_TEMPLATE = """
You are an AI evaluator.
Return ONLY JSON:
{{"scores":{{...}},"feedback":[...],"summary":"..."}}
Score 0-10 for rubric: {rubric_json}
No markdown, no extra text.
Q: {question}
A: {answer}
""".strip()

EVAL_CRITIQUE_TEMPLATE = """
You are a second-pass evaluator.
Review first-pass result and adjust only if needed.
Return ONLY JSON:
{{"scores":{{...}},"feedback":[...],"summary":"..."}}
Rubric: {rubric_json}
Q: {question}
A: {answer}
FirstPass: {first_pass_json}
No markdown, no extra text.
""".strip()

FINAL_REPORT_TEMPLATE = """
You are a hiring manager.
Return ONLY JSON with keys:
overall_recommendation,strengths,weaknesses,final_summary
Profile: {profile_json}
Answers: {answers_json}
No markdown, no extra text.
""".strip()

_CB_LOCK = threading.Lock()
_CB_STATE: Dict[str, Dict[str, float]] = {}


def _safe_json_loads(payload: str, expected_type: type):
    parsed = json.loads(payload)
    if not isinstance(parsed, expected_type):
        raise ValueError(
            f"Expected {expected_type.__name__}, got {type(parsed).__name__}"
        )
    return parsed


def _get_or_init_state_unlocked(provider: str) -> Dict[str, float]:
    if provider not in _CB_STATE:
        _CB_STATE[provider] = {
            "open_until": 0.0,
            "failure_count": 0.0,
            "slow_count": 0.0,
        }
    return _CB_STATE[provider]


def _is_circuit_open(provider: str) -> bool:
    if not LLM_CIRCUIT_BREAKER_ENABLED:
        return False
    with _CB_LOCK:
        state = _get_or_init_state_unlocked(provider)
        return state["open_until"] > time.time()


def _open_circuit(provider: str, reason: str):
    with _CB_LOCK:
        state = _get_or_init_state_unlocked(provider)
        state["open_until"] = time.time() + LLM_CB_OPEN_SECONDS
        state["failure_count"] = 0.0
        state["slow_count"] = 0.0

    logger.warning(
        "LLM circuit opened",
        extra={
            "extra_data": {
                "provider": provider,
                "reason": reason,
                "open_seconds": LLM_CB_OPEN_SECONDS,
            }
        },
    )


def _record_provider_success(provider: str, duration_s: float):
    if not LLM_CIRCUIT_BREAKER_ENABLED:
        return

    should_open = False
    with _CB_LOCK:
        state = _get_or_init_state_unlocked(provider)
        state["failure_count"] = 0.0
        if duration_s >= LLM_CB_SLOW_THRESHOLD_S:
            state["slow_count"] += 1.0
        else:
            state["slow_count"] = 0.0

        if state["slow_count"] >= LLM_CB_SLOW_STRIKES_THRESHOLD:
            should_open = True

    if should_open:
        _open_circuit(provider, "repeated_slow_calls")


def _record_provider_failure(provider: str):
    if not LLM_CIRCUIT_BREAKER_ENABLED:
        return

    should_open = False
    with _CB_LOCK:
        state = _get_or_init_state_unlocked(provider)
        state["failure_count"] += 1.0
        if state["failure_count"] >= LLM_CB_FAILURE_THRESHOLD:
            should_open = True

    if should_open:
        _open_circuit(provider, "repeated_failures")


def _should_fallback(exc: Exception) -> bool:
    if LLM_FALLBACK_ON_ANY_ERROR:
        return True

    msg = str(exc).lower()
    quota_markers = [
        "quota",
        "rate limit",
        "resource exhausted",
        "too many requests",
        "429",
    ]
    return any(marker in msg for marker in quota_markers)


def _provider_order() -> List[str]:
    providers = [LLM_PROVIDER]
    if LLM_AUTO_FALLBACK and LLM_FALLBACK_PROVIDER not in providers:
        providers.append(LLM_FALLBACK_PROVIDER)
    return providers


def _call_gemini(prompt: str, temperature: float, top_p: float = 1.0) -> str:
    if GEMINI_CLIENT is None:
        raise RuntimeError("Gemini is not configured: GOOGLE_API_KEY missing")

    response = GEMINI_CLIENT.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": temperature,
            "top_p": top_p,
        },
    )
    return response.text


def _call_local_qwen(prompt: str, temperature: float, top_p: float = 1.0) -> str:
    payload = {
        "model": LOCAL_LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature, "top_p": top_p},
    }

    request = urllib.request.Request(
        LOCAL_LLM_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=LOCAL_LLM_TIMEOUT_S) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Local LLM request failed: {exc}") from exc

    decoded = _safe_json_loads(body, dict)
    raw = decoded.get("response", "")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Local LLM returned empty response")
    return raw


def _call_provider(provider: str, prompt: str, temperature: float, top_p: float = 1.0) -> str:
    if provider == "gemini":
        return _call_gemini(prompt, temperature, top_p=top_p)
    if provider in {"qwen", "local", "ollama"}:
        return _call_local_qwen(prompt, temperature, top_p=top_p)
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _run_json_task(
    prompt: str, expected_type: type, temperature: float, top_p: float = 1.0
) -> Tuple[Any, str]:
    providers = _provider_order()
    last_error: Exception | None = None

    for index, provider in enumerate(providers):
        if _is_circuit_open(provider):
            logger.warning(
                "LLM provider skipped due to open circuit",
                extra={"extra_data": {"provider": provider}},
            )
            last_error = RuntimeError(f"Provider circuit open: {provider}")
            continue

        provider_start = time.time()
        try:
            raw = _call_provider(provider, prompt, temperature, top_p=top_p)
            elapsed = time.time() - provider_start
            _record_provider_success(provider, elapsed)
            metrics.record_latency(f"llm_provider_{provider}_latency", elapsed)
            parsed = _safe_json_loads(raw, expected_type)
            return parsed, provider
        except Exception as exc:
            _record_provider_failure(provider)
            last_error = exc
            is_last = index == len(providers) - 1
            can_try_next = not is_last and (
                _should_fallback(exc) or _is_circuit_open(provider)
            )

            logger.warning(
                "LLM provider failed",
                extra={
                    "extra_data": {
                        "provider": provider,
                        "error": str(exc),
                        "fallback_next": can_try_next,
                    }
                },
            )

            if can_try_next:
                continue
            raise

    raise RuntimeError("No LLM provider available") from last_error


def _normalize_questions(questions: List[str], num_questions: int) -> List[str]:
    cleaned = [q.strip() for q in questions if isinstance(q, str) and q.strip()]
    if len(cleaned) >= num_questions:
        return cleaned[:num_questions]

    filler = [
        "Tell me about a challenging project you worked on.",
        "What are your strongest technical skills?",
        "How do you stay up-to-date with new technologies?",
        "Where do you see yourself in 5 years?",
    ]
    while len(cleaned) < num_questions:
        cleaned.append(filler[len(cleaned) % len(filler)])
    return cleaned


def generate_questions(
    profile: dict, num_questions: int, temperature_override: float | None = None
) -> List[str]:
    start = time.time()
    temperature = 0.4 if temperature_override is None else temperature_override
    prompt = QUESTION_PROMPT_TEMPLATE.format(
        num_questions=num_questions,
        profile_json=json.dumps(profile, separators=(",", ":")),
    )

    try:
        questions, provider = _run_json_task(prompt, list, temperature=temperature)
        normalized = _normalize_questions(questions, num_questions)

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_question_generation", duration)
        logger.info(
            "Questions generated",
            extra={
                "extra_data": {
                    "provider": provider,
                    "num_questions": len(normalized),
                    "duration": duration,
                }
            },
        )
        return normalized
    except Exception:
        metrics.record_error()
        logger.exception("Question generation failed")
        return _normalize_questions([], num_questions)


def generate_next_question(
    topic: str,
    concept: str,
    difficulty: int,
    strategy: str,
    preferred_skill: str,
    allowed_skills: List[str],
    previous_question: str,
    evaluation_summary: str,
    memory_context: str = "N/A",
    temperature_override: float | None = None,
) -> Tuple[str, str]:
    start = time.time()
    temperature = 0.3 if temperature_override is None else temperature_override
    if not allowed_skills:
        allowed_skills = [preferred_skill or "Machine Learning"]
    if preferred_skill not in allowed_skills:
        preferred_skill = allowed_skills[0]
    prompt = NEXT_QUESTION_PROMPT_TEMPLATE.format(
        topic=topic,
        concept=concept.strip() or "N/A",
        difficulty=max(1, min(3, int(difficulty))),
        strategy=strategy,
        preferred_skill=preferred_skill.strip() or "N/A",
        allowed_skills_json=json.dumps(allowed_skills, separators=(",", ":")),
        previous_question=previous_question.strip() or "N/A",
        evaluation_summary=evaluation_summary.strip() or "N/A",
        memory_context=memory_context.strip() or "N/A",
    )

    try:
        payload, provider = _run_json_task(prompt, dict, temperature=temperature, top_p=0.85)
        question = payload.get("question", "")
        generated_skill = payload.get("skill", preferred_skill)
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Next-question payload missing question")
        if not isinstance(generated_skill, str) or not generated_skill.strip():
            generated_skill = preferred_skill
        generated_skill = generated_skill.strip()
        if generated_skill not in allowed_skills:
            generated_skill = preferred_skill if preferred_skill in allowed_skills else allowed_skills[0]

        result = question.strip()
        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_next_question_generation", duration)
        logger.info(
            "Next question generated",
            extra={
                "extra_data": {
                    "provider": provider,
                    "topic": topic,
                    "difficulty": difficulty,
                    "strategy": strategy,
                    "skill": generated_skill,
                    "duration": duration,
                }
            },
        )
        return result, generated_skill
    except Exception:
        metrics.record_error()
        logger.exception("Next question generation failed")
        fallback = {
            "python": "Can you explain a Python concept you used recently?",
            "machine_learning": "How would you evaluate a machine learning model?",
            "deep_learning": "What is the purpose of an activation function in neural networks?",
            "system_design": "How would you design a scalable API for high traffic?",
        }
        return fallback.get(topic, "Can you explain this topic in more depth with an example?"), preferred_skill


def prepare_evaluation_context(profile: dict, question: str, lightweight: bool) -> dict:
    return {
        "question": question,
        "rubric_json": RUBRIC_JSON_LITE if lightweight else RUBRIC_JSON_FULL,
        "lightweight": lightweight,
    }


def _clamp_scores(scores: Dict[str, Any], rubric: List[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for key in rubric:
        raw = scores.get(key, 0)
        try:
            value = int(raw)
        except Exception:
            value = 0
        result[key] = max(0, min(10, value))
    return result


def _score_variance(a: Dict[str, int], b: Dict[str, int]) -> float:
    keys = list(set(a.keys()).union(set(b.keys())))
    if not keys:
        return 0.0
    diffs = [(a.get(k, 0) - b.get(k, 0)) ** 2 for k in keys]
    return mean(diffs)


def evaluate_answer(
    question: str,
    answer: str,
    profile: dict,
    lightweight: bool = False,
    temperature_override: float | None = None,
    prepared_context: dict | None = None,
) -> dict:
    start = time.time()
    base_temperature = 0.1 if temperature_override is None else temperature_override
    context = prepared_context or prepare_evaluation_context(profile, question, lightweight)
    rubric = RUBRIC_LITE if context["lightweight"] else RUBRIC_FULL

    eval_prompt = EVAL_PROMPT_TEMPLATE.format(
        rubric_json=context["rubric_json"],
        question=context["question"],
        answer=answer,
    )

    try:
        first_pass, provider = _run_json_task(
            eval_prompt, dict, temperature=base_temperature, top_p=0.8
        )
        first_scores = _clamp_scores(first_pass.get("scores", {}), rubric)

        final_eval = first_pass
        final_scores = first_scores
        critique_used = False

        if EVAL_MULTI_PASS and not lightweight:
            critique_prompt = EVAL_CRITIQUE_TEMPLATE.format(
                rubric_json=context["rubric_json"],
                question=context["question"],
                answer=answer,
                first_pass_json=json.dumps(first_pass, separators=(",", ":")),
            )
            critique_pass, _ = _run_json_task(
                critique_prompt,
                dict,
                temperature=max(0.05, base_temperature - 0.05),
                top_p=0.8,
            )
            critique_scores = _clamp_scores(critique_pass.get("scores", {}), rubric)
            final_eval = critique_pass
            final_scores = critique_scores
            critique_used = True

        variance = 0.0
        consistency_scores = final_scores
        if EVAL_SELF_CONSISTENCY:
            consistency_pass, _ = _run_json_task(
                eval_prompt,
                dict,
                temperature=min(0.45, base_temperature + 0.12),
                top_p=0.8,
            )
            consistency_scores = _clamp_scores(consistency_pass.get("scores", {}), rubric)
            variance = _score_variance(final_scores, consistency_scores)

        confidence_score = round(1.0 / (1.0 + variance), 3)

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_evaluation", duration)

        evaluation = {
            "scores": final_scores,
            "feedback": final_eval.get("feedback", []),
            "summary": final_eval.get("summary", ""),
            "confidence_score": confidence_score,
            "evaluator_variance": round(variance, 3),
            "meta": {
                "provider": provider,
                "critique_used": critique_used,
                "self_consistency_used": EVAL_SELF_CONSISTENCY,
            },
        }

        logger.info(
            "Answer evaluated",
            extra={
                "extra_data": {
                    "provider": provider,
                    "duration": duration,
                    "scores": evaluation.get("scores", {}),
                    "answer_length": len(answer),
                    "confidence": confidence_score,
                }
            },
        )
        return evaluation
    except Exception:
        metrics.record_error()
        logger.exception("Evaluation failed")
        fallback_scores = {name: 5 for name in rubric}
        return {
            "scores": fallback_scores,
            "feedback": ["Evaluation fallback triggered."],
            "summary": "AI evaluation failed.",
            "confidence_score": 0.2,
            "evaluator_variance": 3.0,
            "meta": {
                "provider": "fallback",
                "critique_used": False,
                "self_consistency_used": False,
            },
        }


def generate_final_report(profile: dict, answers: List[dict]) -> dict:
    start = time.time()
    prompt = FINAL_REPORT_TEMPLATE.format(
        profile_json=json.dumps(profile, separators=(",", ":")),
        answers_json=json.dumps(answers, separators=(",", ":")),
    )

    try:
        report, provider = _run_json_task(prompt, dict, temperature=0.2)
        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_final_report", duration)
        logger.info(
            "Final report generated",
            extra={
                "extra_data": {
                    "provider": provider,
                    "duration": duration,
                    "num_answers": len(answers),
                }
            },
        )
        return report
    except Exception:
        metrics.record_error()
        logger.exception("Final report generation failed")
        return {"error": "Failed to generate report."}


def prewarm_llm():
    """
    Best-effort prewarm to reduce first request latency.
    """
    prompt = '{"status":"ok"}'
    try:
        providers = _provider_order()
        for provider in providers:
            if _is_circuit_open(provider):
                continue
            started = time.time()
            raw = _call_provider(provider, prompt, temperature=0.0)
            parsed = _safe_json_loads(raw, dict)
            if parsed.get("status") != "ok":
                raise ValueError("Prewarm response missing status=ok")
            _record_provider_success(provider, time.time() - started)
            metrics.record_latency("llm_prewarm", time.time() - started)
            logger.info(
                "LLM prewarm successful",
                extra={"extra_data": {"provider": provider}},
            )
            return
    except Exception:
        metrics.record_error()
        logger.exception("LLM prewarm failed")
