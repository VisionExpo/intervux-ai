import json
import os
import threading
import time
import urllib.error
import urllib.request
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


def _call_gemini(prompt: str, temperature: float) -> str:
    if GEMINI_CLIENT is None:
        raise RuntimeError("Gemini is not configured: GOOGLE_API_KEY missing")

    response = GEMINI_CLIENT.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": temperature,
        },
    )
    return response.text


def _call_local_qwen(prompt: str, temperature: float) -> str:
    payload = {
        "model": LOCAL_LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
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


def _call_provider(provider: str, prompt: str, temperature: float) -> str:
    if provider == "gemini":
        return _call_gemini(prompt, temperature)
    if provider in {"qwen", "local", "ollama"}:
        return _call_local_qwen(prompt, temperature)
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _run_json_task(
    prompt: str, expected_type: type, temperature: float
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
            raw = _call_provider(provider, prompt, temperature)
            _record_provider_success(provider, time.time() - provider_start)
            metrics.record_latency(
                f"llm_provider_{provider}_latency", time.time() - provider_start
            )
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
    temperature = 0.7 if temperature_override is None else temperature_override
    prompt = f"""
    You are an expert AI interviewer. Based on the following candidate profile,
    generate exactly {num_questions} technical interview questions.
    Return ONLY valid JSON as a list of strings.
    Do not include markdown fences, labels, or explanations.

    Candidate Profile:
    {json.dumps(profile, indent=2)}
    """

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


def evaluate_answer(
    question: str,
    answer: str,
    profile: dict,
    lightweight: bool = False,
    temperature_override: float | None = None,
) -> dict:
    start = time.time()
    temperature = 0.3 if temperature_override is None else temperature_override
    criteria = """
    - Technical Accuracy
    - Clarity of Explanation
    - Depth of Understanding
    - Confidence & Communication
    """
    if lightweight:
        criteria = """
    - Technical Accuracy
    - Clarity of Explanation
    """

    prompt = f"""
    You are an expert AI interviewer evaluating a candidate's answer.
    Score 0-10 on these dimensions:
    {criteria}

    Return ONLY valid JSON with this exact structure:
    {{
      "scores": {{ ... }},
      "feedback": [...],
      "summary": "..."
    }}
    Do not include markdown fences, labels, or explanations.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Question:
    "{question}"

    Answer:
    "{answer}"
    """

    try:
        evaluation, provider = _run_json_task(prompt, dict, temperature=temperature)
        if "scores" in evaluation and isinstance(evaluation["scores"], dict):
            for key, value in evaluation["scores"].items():
                evaluation["scores"][key] = max(0, min(10, int(value)))

        duration = round(time.time() - start, 3)
        metrics.record_latency("llm_evaluation", duration)
        logger.info(
            "Answer evaluated",
            extra={
                "extra_data": {
                    "provider": provider,
                    "duration": duration,
                    "scores": evaluation.get("scores", {}),
                    "answer_length": len(answer),
                }
            },
        )
        return evaluation
    except Exception:
        metrics.record_error()
        logger.exception("Evaluation failed")
        return {
            "scores": {
                "Technical Accuracy": 5,
                "Clarity of Explanation": 5,
                "Depth of Understanding": 5 if not lightweight else 0,
                "Confidence & Communication": 5 if not lightweight else 0,
            },
            "feedback": ["Evaluation fallback triggered."],
            "summary": "AI evaluation failed.",
        }


def generate_final_report(profile: dict, answers: List[dict]) -> dict:
    start = time.time()
    prompt = f"""
    You are a hiring manager writing a final report.
    Provide:
    - Overall Recommendation
    - Strengths
    - Weaknesses
    - Final Summary

    Return ONLY valid JSON.
    Do not include markdown fences, labels, or explanations.

    Candidate Profile:
    {json.dumps(profile, indent=2)}

    Q&A:
    {json.dumps(answers, indent=2)}
    """

    try:
        report, provider = _run_json_task(prompt, dict, temperature=0.4)
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
    prompt = (
        'Return ONLY valid JSON: {"status":"ok"} '
        "Do not include markdown or any extra text."
    )
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
