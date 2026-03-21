from __future__ import annotations

from typing import Any, Dict, List, Tuple

from backend.core.llm_brain import generate_next_question
from backend.core.knowledge_graph import GRAPH, next_node
from backend.core.skill_coverage import SkillCoverageEngine

DEFAULT_TOPICS = [
    "python",
    "machine_learning",
    "deep_learning",
    "system_design",
    "javascript",
    "java",
    "databases",
    "devops",
    "backend",
]
DEFAULT_SKILLS = [
    "Python",
    "Machine Learning",
    "Deep Learning",
    "System Design",
    "JavaScript",
    "Java",
    "Databases",
    "DevOps",
    "Backend",
]
SKILL_TO_TOPIC = {
    "Python": "python",
    "Machine Learning": "machine_learning",
    "Deep Learning": "deep_learning",
    "System Design": "system_design",
    "JavaScript": "javascript",
    "Java": "java",
    "Databases": "databases",
    "DevOps": "devops",
    "Backend": "backend",
}
TOPIC_TO_SKILL = {value: key for key, value in SKILL_TO_TOPIC.items()}

_TOPIC_ALIASES = {
    "python": {"python", "django", "flask", "fastapi", "celery", "sqlalchemy"},
    "machine_learning": {"machine learning", "ml", "scikit", "xgboost", "pandas", "numpy"},
    "deep_learning": {"deep learning", "pytorch", "tensorflow", "cnn", "rnn", "transformer", "llm"},
    "system_design": {"system design", "architecture", "microservices", "scalability", "distributed"},
    "javascript": {"javascript", "typescript", "react", "vue", "angular", "node", "nextjs", "nodejs"},
    "java": {"java", "spring", "springboot", "maven", "gradle", "jvm", "kotlin"},
    "databases": {"sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "database"},
    "devops": {"docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "terraform", "linux"},
    "backend": {"api", "rest", "graphql", "grpc", "fastapi", "express", "backend"},
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


def build_skill_coverage_engine(profile: Dict[str, Any]) -> SkillCoverageEngine:
    discovered: List[str] = []
    topic_map = build_skill_map(profile)
    for topic in topic_map.keys():
        discovered.append(TOPIC_TO_SKILL.get(topic, "Machine Learning"))
    if not discovered:
        discovered = list(DEFAULT_SKILLS)
    return SkillCoverageEngine(discovered)


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
    next_skill = TOPIC_TO_SKILL.get(next_topic, "Machine Learning")
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

    question, _skill = generate_next_question(
        topic=next_topic,
        concept=_topic_default_concept(next_topic),
        difficulty=next_difficulty,
        strategy=strategy,
        preferred_skill=next_skill,
        allowed_skills=list(DEFAULT_SKILLS),
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
    coverage_engine: SkillCoverageEngine | None,
    difficulty: int,
    last_topic: str | None,
    last_skill: str | None,
    last_question: str,
    evaluation_summary: str,
    question_temperature: float,
    memory_context: str = "N/A",
    current_concept: str | None = None,
) -> Tuple[str, str, str, str, int, str, int]:
    if coverage_engine is not None and coverage_engine.skills:
        skill = coverage_engine.next_skill()
        topic = SKILL_TO_TOPIC.get(skill, "machine_learning")
    else:
        topic = select_next_topic(skill_map, topic_scores, last_topic)
        skill = TOPIC_TO_SKILL.get(topic, "Machine Learning")

    strategy = select_strategy(score, confidence)
    if _is_unbalanced_coverage(skill_map) and skill_map.get(topic, 0) <= 0:
        strategy = "topic_shift"

    next_difficulty = max(1, min(3, int(difficulty)))

    concept = _select_next_concept(topic, current_concept, score, next_difficulty)
    concept_difficulty = _concept_difficulty(concept, next_difficulty)

    question, generated_skill = generate_next_question(
        topic=topic,
        concept=concept,
        difficulty=next_difficulty,
        strategy=strategy,
        preferred_skill=skill,
        allowed_skills=list(coverage_engine.skills.keys()) if coverage_engine else list(DEFAULT_SKILLS),
        previous_question=last_question,
        evaluation_summary=evaluation_summary,
        memory_context=memory_context,
        temperature_override=question_temperature,
    )
    skill = generated_skill if generated_skill else skill
    topic = SKILL_TO_TOPIC.get(skill, topic)

    skill_map[topic] = skill_map.get(topic, 0) + 1
    return question, skill, topic, strategy, next_difficulty, concept, concept_difficulty


def generate_initial_question(
    skill_map: Dict[str, int],
    coverage_engine: SkillCoverageEngine | None,
    question_temperature: float,
    memory_context: str = "N/A",
    start_difficulty: int = 2,
) -> Tuple[str, str, str, str, int, str, int]:
    if coverage_engine is not None and coverage_engine.skills:
        skill = coverage_engine.next_skill()
        topic = SKILL_TO_TOPIC.get(skill, "machine_learning")
    else:
        topic = select_next_topic(skill_map, topic_scores={}, last_topic=None)
        skill = TOPIC_TO_SKILL.get(topic, "Machine Learning")

    strategy = "explore"
    difficulty = max(1, min(3, int(start_difficulty)))
    concept = _topic_default_concept(topic)
    concept_difficulty = _concept_difficulty(concept, difficulty)
    question, generated_skill = generate_next_question(
        topic=topic,
        concept=concept,
        difficulty=difficulty,
        strategy=strategy,
        preferred_skill=skill,
        allowed_skills=list(coverage_engine.skills.keys()) if coverage_engine else list(DEFAULT_SKILLS),
        previous_question="N/A",
        evaluation_summary="N/A",
        memory_context=memory_context,
        temperature_override=question_temperature,
    )
    skill = generated_skill if generated_skill else skill
    topic = SKILL_TO_TOPIC.get(skill, topic)
    skill_map[topic] = skill_map.get(topic, 0) + 1
    return question, skill, topic, strategy, difficulty, concept, concept_difficulty


def _topic_default_concept(topic: str) -> str:
    if topic == "machine_learning":
        return "Machine Learning"
    if topic == "deep_learning":
        return "CNN"
    if topic == "python":
        return "Python"
    if topic == "system_design":
        return "System Design"
    if topic == "javascript":
        return "JavaScript"
    if topic == "java":
        return "Java"
    if topic == "databases":
        return "Databases"
    if topic == "devops":
        return "DevOps"
    if topic == "backend":
        return "Backend"
    return topic.replace("_", " ").title()


def _concept_difficulty(concept: str, fallback: int) -> int:
    node = GRAPH.nodes.get(concept)
    if node is None:
        return max(1, min(3, int(fallback)))
    return max(1, min(3, int(node.difficulty)))


def _select_next_concept(
    topic: str, current_concept: str | None, score: float, difficulty: int
) -> str:
    if topic not in {"machine_learning", "deep_learning"}:
        return _topic_default_concept(topic)

    if current_concept and current_concept in GRAPH.nodes:
        current_node = GRAPH.nodes[current_concept]
    else:
        default = _topic_default_concept(topic)
        current_node = GRAPH.nodes.get(default) or GRAPH.nodes.get("Machine Learning")

    target = next_node(current_node, score)
    if target is not None and _concept_difficulty(target.name, difficulty) == difficulty:
        return target.name

    difficulty_nodes = [
        node.name
        for node in GRAPH.nodes.values()
        if _concept_difficulty(node.name, difficulty) == difficulty
    ]
    if difficulty_nodes:
        for name in difficulty_nodes:
            if topic == "deep_learning" and name in {"CNN", "Transformers", "Batch Normalization", "Dropout"}:
                return name
            if topic == "machine_learning" and name in {"Machine Learning", "Supervised Learning", "Gradient Descent", "Learning Rate"}:
                return name
        return difficulty_nodes[0]

    if target is None:
        return _topic_default_concept(topic)
    return target.name
