from __future__ import annotations

from typing import Any, Dict, List, Tuple

from backend.core.llm_brain import generate_next_question

DEFAULT_TOPICS = [
    "python",
    "machine_learning",
    "deep_learning",
    "system_design",
]

_TOPIC_ALIASES = {
    "python": {"python", "django", "flask", "fastapi"},
    "machine_learning": {"machine learning", "ml", "scikit", "xgboost"},
    "deep_learning": {"deep learning", "pytorch", "tensorflow", "cnn", "rnn", "transformer"},
    "system_design": {"system design", "architecture", "microservices", "scalability"},
}


def _normalize_text(value: str) -> str:
    return value.strip().lower().replace("-", " ").replace("_", " ")


def _match_topic(skill: str) -> str | None:
    raw = _normalize_text(skill)
    for topic, aliases in _TOPIC_ALIASES.items():
        if raw in aliases:
            return topic
        for alias in aliases:
            if alias in raw:
                return topic
    return None


def build_skill_map(profile: Dict[str, Any]) -> Dict[str, int]:
    skill_map: Dict[str, int] = {}
    skills = profile.get("skills", [])
    for item in skills:
        if not isinstance(item, str):
            continue
        topic = _match_topic(item)
        if topic:
            skill_map[topic] = 0

    projects = profile.get("projects", [])
    for project in projects:
        if not isinstance(project, dict):
            continue
        for tech in project.get("tech_stack", []):
            if not isinstance(tech, str):
                continue
            topic = _match_topic(tech)
            if topic:
                skill_map[topic] = 0

    if not skill_map:
        for topic in DEFAULT_TOPICS:
            skill_map[topic] = 0
    return skill_map


def _evaluation_score(evaluation: Dict[str, Any]) -> float:
    scores = evaluation.get("scores", {})
    if not isinstance(scores, dict) or not scores:
        return 5.0
    values: List[float] = []
    for value in scores.values():
        try:
            values.append(float(value))
        except Exception:
            continue
    if not values:
        return 5.0
    return sum(values) / len(values)


def update_topic_scores(
    topic_scores: Dict[str, List[float]], topic: str, evaluation: Dict[str, Any]
) -> float:
    score = _evaluation_score(evaluation)
    topic_scores.setdefault(topic, []).append(score)
    values = topic_scores[topic]
    return sum(values) / len(values)


def adjust_difficulty(current: int, average_score: float) -> int:
    difficulty = current
    if average_score >= 8.0:
        difficulty += 1
    elif average_score <= 4.0:
        difficulty -= 1
    return max(1, min(3, difficulty))


def select_strategy(score: float, confidence: float) -> str:
    if confidence < 0.4 and score <= 4.0:
        return "rephrase_verify"
    if confidence < 0.4:
        return "clarify"
    if score >= 8.0:
        return "deep_dive"
    if score <= 4.0:
        return "simplify"
    return "follow_up"


def _is_unbalanced_coverage(skill_map: Dict[str, int]) -> bool:
    if not skill_map:
        return False
    values = list(skill_map.values())
    return (max(values) - min(values)) >= 2


def select_next_topic(
    skill_map: Dict[str, int],
    topic_scores: Dict[str, List[float]],
    last_topic: str | None,
) -> str:
    if not skill_map:
        return DEFAULT_TOPICS[0]

    uncovered = [topic for topic, count in skill_map.items() if count <= 0]
    if uncovered:
        return sorted(uncovered)[0]

    weak_topics: List[Tuple[float, str]] = []
    for topic in skill_map.keys():
        values = topic_scores.get(topic, [])
        if values:
            avg = sum(values) / len(values)
            weak_topics.append((avg, topic))
    weak_topics.sort(key=lambda pair: pair[0])
    if weak_topics and weak_topics[0][0] < 6.0:
        return weak_topics[0][1]

    by_coverage = sorted(skill_map.items(), key=lambda pair: pair[1])
    for topic, _count in by_coverage:
        if topic != last_topic:
            return topic
    return by_coverage[0][0]


def generate_adaptive_question(
    profile: Dict[str, Any],
    skill_map: Dict[str, int],
    topic_scores: Dict[str, List[float]],
    last_topic: str | None,
    last_question: str,
    evaluation: Dict[str, Any],
    current_difficulty: int,
    question_temperature: float,
    memory_context: str = "N/A",
) -> Tuple[str, str, str, int]:
    _ = profile
    next_topic = select_next_topic(skill_map, topic_scores, last_topic)
    score = _evaluation_score(evaluation)
    confidence = float(evaluation.get("confidence_score", 0.7) or 0.7)
    strategy = select_strategy(score, confidence)
    if _is_unbalanced_coverage(skill_map) and skill_map.get(next_topic, 0) <= 0:
        strategy = "topic_shift"
    next_topic_values = topic_scores.get(next_topic, [])
    if next_topic_values:
        topic_avg = sum(next_topic_values) / len(next_topic_values)
    else:
        topic_avg = score
    next_difficulty = adjust_difficulty(current_difficulty, topic_avg)

    summary = evaluation.get("summary", "")
    if not isinstance(summary, str):
        summary = ""

    question = generate_next_question(
        topic=next_topic,
        difficulty=next_difficulty,
        strategy=strategy,
        previous_question=last_question,
        evaluation_summary=summary,
        memory_context=memory_context,
        temperature_override=question_temperature,
    )

    skill_map[next_topic] = skill_map.get(next_topic, 0) + 1
    return question, next_topic, strategy, next_difficulty


def next_question(
    score: float,
    confidence: float,
    topic_scores: Dict[str, List[float]],
    skill_map: Dict[str, int],
    difficulty: int,
    last_topic: str | None,
    last_question: str,
    evaluation_summary: str,
    question_temperature: float,
    memory_context: str = "N/A",
) -> Tuple[str, str, str, int]:
    topic = select_next_topic(skill_map, topic_scores, last_topic)
    strategy = select_strategy(score, confidence)
    if _is_unbalanced_coverage(skill_map) and skill_map.get(topic, 0) <= 0:
        strategy = "topic_shift"

    topic_values = topic_scores.get(topic, [])
    topic_avg = (sum(topic_values) / len(topic_values)) if topic_values else score
    next_difficulty = adjust_difficulty(difficulty, topic_avg)

    question = generate_next_question(
        topic=topic,
        difficulty=next_difficulty,
        strategy=strategy,
        previous_question=last_question,
        evaluation_summary=evaluation_summary,
        memory_context=memory_context,
        temperature_override=question_temperature,
    )

    skill_map[topic] = skill_map.get(topic, 0) + 1
    return question, topic, strategy, next_difficulty


def generate_initial_question(
    skill_map: Dict[str, int],
    question_temperature: float,
    memory_context: str = "N/A",
) -> Tuple[str, str, str, int]:
    topic = select_next_topic(skill_map, topic_scores={}, last_topic=None)
    strategy = "explore"
    difficulty = 2
    question = generate_next_question(
        topic=topic,
        difficulty=difficulty,
        strategy=strategy,
        previous_question="N/A",
        evaluation_summary="N/A",
        memory_context=memory_context,
        temperature_override=question_temperature,
    )
    skill_map[topic] = skill_map.get(topic, 0) + 1
    return question, topic, strategy, difficulty
