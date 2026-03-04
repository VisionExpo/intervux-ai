import os
import re
from typing import Any, Dict, List

MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "5"))

_PHRASE_HINTS = [
    "gradient descent",
    "learning rate",
    "batch normalization",
    "neural network",
    "recommendation system",
    "system design",
    "microservices",
    "feature engineering",
    "regularization",
    "overfitting",
    "underfitting",
    "cross validation",
    "dropout",
    "backpropagation",
    "transformer",
    "cnn",
    "rnn",
    "lstm",
]


def _average_score(scores: Dict[str, Any]) -> float:
    values: List[float] = []
    for value in scores.values():
        try:
            values.append(float(value))
        except Exception:
            continue
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def extract_key_concepts(answer: str) -> List[str]:
    text = answer.lower()
    concepts: List[str] = []

    for phrase in _PHRASE_HINTS:
        if phrase in text:
            concepts.append(phrase)

    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_+\-]{2,}", answer)
    for token in tokens:
        lower = token.lower()
        if lower.isdigit():
            continue
        if lower in {"the", "and", "that", "with", "from", "this", "have", "about"}:
            continue
        if token.isupper() and len(token) <= 6:
            concepts.append(token)

    deduped: List[str] = []
    seen = set()
    for concept in concepts:
        key = concept.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(concept.strip())
    return deduped[:12]


def update_memory(memory, question: str, answer: str, evaluation: Dict[str, Any], topic: str):
    scores = evaluation.get("scores", {})
    if not isinstance(scores, dict):
        scores = {}

    confidence = evaluation.get("confidence_score", evaluation.get("confidence", 0.0))
    try:
        confidence_value = float(confidence)
    except Exception:
        confidence_value = 0.0

    memory.answers.append(
        {
            "question": question,
            "answer": answer,
            "score": scores,
            "avg_score": _average_score(scores),
            "confidence": round(confidence_value, 2),
            "summary": str(evaluation.get("summary", "") or ""),
        }
    )
    memory.answers = memory.answers[-MAX_MEMORY_ITEMS:]

    concepts = extract_key_concepts(answer)
    memory.key_concepts.update(concepts)

    memory.last_topics.append(topic)
    memory.last_topics = memory.last_topics[-MAX_MEMORY_ITEMS:]


def seed_memory_projects(memory, profile: Dict[str, Any]):
    projects = profile.get("projects", [])
    names: List[str] = []
    for item in projects:
        if isinstance(item, dict):
            title = item.get("title")
            if isinstance(title, str) and title.strip():
                names.append(title.strip())
    memory.projects = names[:MAX_MEMORY_ITEMS]


def build_memory_context(memory) -> str:
    concepts = sorted(list(memory.key_concepts))[:12]
    recent_answers = memory.answers[-MAX_MEMORY_ITEMS:]

    lines: List[str] = []
    lines.append("Candidate Concepts Mentioned:")
    if concepts:
        lines.extend([f"- {item}" for item in concepts])
    else:
        lines.append("- N/A")

    lines.append("Recent Answers:")
    if recent_answers:
        for item in recent_answers:
            q = str(item.get("question", "")).strip()
            avg = item.get("avg_score", 0.0)
            conf = item.get("confidence", 0.0)
            lines.append(f"- Q: {q[:120]} | avg_score={avg} | confidence={conf}")
    else:
        lines.append("- N/A")

    lines.append("Projects:")
    if memory.projects:
        lines.extend([f"- {item}" for item in memory.projects[:MAX_MEMORY_ITEMS]])
    else:
        lines.append("- N/A")

    return "\n".join(lines)
