from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from fastapi import HTTPException

from backend.models.recruiter_dashboard import (
    Candidate,
    CandidateComparisonRow,
    CandidateInterviewReport,
    InterviewSummary,
    QuestionBreakdown,
    ReplayEvaluation,
    ReplaySegment,
    SkillAnalytics,
)


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


_CANDIDATES: List[Candidate] = [
    Candidate(
        id="11321f7f-9b8b-4d32-a573-8e0cbe4de401",
        name="John Doe",
        email="john.doe@example.com",
        role="Python Engineer",
        resume_url="https://example.com/resumes/john-doe.pdf",
        created_at=_dt("2026-02-18T09:30:00"),
    ),
    Candidate(
        id="3d6e1d62-2b6f-4174-b996-2f2ffb7f3d77",
        name="Jane Smith",
        email="jane.smith@example.com",
        role="ML Engineer",
        resume_url="https://example.com/resumes/jane-smith.pdf",
        created_at=_dt("2026-02-20T11:10:00"),
    ),
    Candidate(
        id="8b0c8f8f-8912-4d3d-b26f-1d503027e0a5",
        name="Mike Lee",
        email="mike.lee@example.com",
        role="Backend Engineer",
        resume_url="https://example.com/resumes/mike-lee.pdf",
        created_at=_dt("2026-02-22T14:05:00"),
    ),
]

_INTERVIEWS: Dict[str, InterviewSummary] = {
    "8f8703a6-b359-4289-8f6b-6e8e8fcb5301": InterviewSummary(
        id="8f8703a6-b359-4289-8f6b-6e8e8fcb5301",
        candidate_id="11321f7f-9b8b-4d32-a573-8e0cbe4de401",
        role="Python Engineer",
        overall_score=82.0,
        technical_score=85.0,
        communication_score=78.0,
        problem_solving_score=80.0,
        started_at=_dt("2026-02-25T10:00:00"),
        completed_at=_dt("2026-02-25T10:40:00"),
    ),
    "f64df56d-ce9f-4a08-99cc-9d28baf0948c": InterviewSummary(
        id="f64df56d-ce9f-4a08-99cc-9d28baf0948c",
        candidate_id="3d6e1d62-2b6f-4174-b996-2f2ffb7f3d77",
        role="ML Engineer",
        overall_score=88.0,
        technical_score=90.0,
        communication_score=85.0,
        problem_solving_score=89.0,
        started_at=_dt("2026-02-26T12:00:00"),
        completed_at=_dt("2026-02-26T12:45:00"),
    ),
    "a011f26a-0b6f-4319-9f12-97535a2ece8f": InterviewSummary(
        id="a011f26a-0b6f-4319-9f12-97535a2ece8f",
        candidate_id="8b0c8f8f-8912-4d3d-b26f-1d503027e0a5",
        role="Backend Engineer",
        overall_score=72.0,
        technical_score=70.0,
        communication_score=75.0,
        problem_solving_score=71.0,
        started_at=_dt("2026-02-27T09:15:00"),
        completed_at=_dt("2026-02-27T09:55:00"),
    ),
}

_QUESTIONS: Dict[str, List[QuestionBreakdown]] = {
    "8f8703a6-b359-4289-8f6b-6e8e8fcb5301": [
        QuestionBreakdown(
            id="9f4e4dd2-30da-4486-8682-f32485f0f1e2",
            interview_id="8f8703a6-b359-4289-8f6b-6e8e8fcb5301",
            question="Explain quicksort.",
            answer="Quicksort recursively partitions the array around a pivot.",
            score=8.5,
            feedback="Good understanding and complexity explanation.",
        ),
        QuestionBreakdown(
            id="36a88b8f-38b3-4f14-b56c-c1de0674fff9",
            interview_id="8f8703a6-b359-4289-8f6b-6e8e8fcb5301",
            question="What are Python generators?",
            answer="Generators yield lazily and preserve state across iterations.",
            score=7.0,
            feedback="Solid fundamentals, but needed stronger real-world examples.",
        ),
        QuestionBreakdown(
            id="6964d30e-ad4a-4f97-95c4-f0f335f2444d",
            interview_id="8f8703a6-b359-4289-8f6b-6e8e8fcb5301",
            question="Design a URL shortener service.",
            answer="Used hash ids, rate limits, and replication plan.",
            score=9.0,
            feedback="Strong tradeoff analysis and scaling strategy.",
        ),
    ],
    "f64df56d-ce9f-4a08-99cc-9d28baf0948c": [
        QuestionBreakdown(
            id="5af8fd4d-4a30-4f8e-9ca4-4db5f6955f16",
            interview_id="f64df56d-ce9f-4a08-99cc-9d28baf0948c",
            question="How do you detect overfitting in production?",
            answer="Monitor drift metrics and validation gap trends.",
            score=8.8,
            feedback="Good production signal coverage.",
        ),
        QuestionBreakdown(
            id="713d9a29-f950-41ea-880b-8432f6db6410",
            interview_id="f64df56d-ce9f-4a08-99cc-9d28baf0948c",
            question="Explain attention in transformers.",
            answer="Self-attention weights token relevance for contextual encoding.",
            score=9.1,
            feedback="Clear conceptual understanding with examples.",
        ),
    ],
    "a011f26a-0b6f-4319-9f12-97535a2ece8f": [
        QuestionBreakdown(
            id="ea8f9aca-1bf3-4503-9d9d-76f605a95db6",
            interview_id="a011f26a-0b6f-4319-9f12-97535a2ece8f",
            question="Explain transaction isolation levels.",
            answer="Described read committed and serializable with tradeoffs.",
            score=7.2,
            feedback="Correct concepts, limited examples.",
        ),
        QuestionBreakdown(
            id="6370d8af-ea2c-4de5-a8ff-5156a82d5957",
            interview_id="a011f26a-0b6f-4319-9f12-97535a2ece8f",
            question="How would you debug a latency spike?",
            answer="Start with tracing, then break down by service and DB.",
            score=7.0,
            feedback="Reasonable process but lacked prioritization detail.",
        ),
    ],
}

_REPLAY_SEGMENTS: Dict[str, List[ReplaySegment]] = {
    "8f8703a6-b359-4289-8f6b-6e8e8fcb5301": [
        ReplaySegment(
            question="Explain quicksort.",
            candidate_audio="s3://audio/john-doe-answer-1.wav",
            transcript="Quicksort is a divide and conquer algorithm that partitions by pivot.",
            evaluation=ReplayEvaluation(technical=8.5, clarity=7.5, reasoning=8.0),
        ),
        ReplaySegment(
            question="What are Python generators?",
            candidate_audio="s3://audio/john-doe-answer-2.wav",
            transcript="A generator yields values one at a time, reducing memory usage.",
            evaluation=ReplayEvaluation(technical=7.0, clarity=7.0, reasoning=7.2),
        ),
    ],
    "f64df56d-ce9f-4a08-99cc-9d28baf0948c": [
        ReplaySegment(
            question="Explain attention in transformers.",
            candidate_audio="s3://audio/jane-smith-answer-2.wav",
            transcript="Attention lets each token attend to others through learned weights.",
            evaluation=ReplayEvaluation(technical=9.1, clarity=8.8, reasoning=8.9),
        ),
    ],
    "a011f26a-0b6f-4319-9f12-97535a2ece8f": [
        ReplaySegment(
            question="How would you debug a latency spike?",
            candidate_audio="s3://audio/mike-lee-answer-2.wav",
            transcript="I would inspect traces, service saturation, and database locks.",
            evaluation=ReplayEvaluation(technical=7.0, clarity=7.4, reasoning=7.1),
        ),
    ],
}

_ANALYTICS: Dict[str, SkillAnalytics] = {
    "8f8703a6-b359-4289-8f6b-6e8e8fcb5301": SkillAnalytics(
        interview_id="8f8703a6-b359-4289-8f6b-6e8e8fcb5301",
        skills={
            "python": 82.0,
            "data_structures": 75.0,
            "system_design": 68.0,
            "communication": 80.0,
            "problem_solving": 79.0,
        },
    ),
    "f64df56d-ce9f-4a08-99cc-9d28baf0948c": SkillAnalytics(
        interview_id="f64df56d-ce9f-4a08-99cc-9d28baf0948c",
        skills={
            "python": 86.0,
            "machine_learning": 92.0,
            "system_design": 78.0,
            "communication": 85.0,
            "problem_solving": 89.0,
        },
    ),
    "a011f26a-0b6f-4319-9f12-97535a2ece8f": SkillAnalytics(
        interview_id="a011f26a-0b6f-4319-9f12-97535a2ece8f",
        skills={
            "python": 68.0,
            "databases": 73.0,
            "system_design": 70.0,
            "communication": 75.0,
            "problem_solving": 71.0,
        },
    ),
}

_CANDIDATE_TO_INTERVIEW = {value.candidate_id: key for key, value in _INTERVIEWS.items()}
_CANDIDATES_BY_ID = {candidate.id: candidate for candidate in _CANDIDATES}


def list_candidates() -> List[dict]:
    return [
        {
            **candidate.model_dump(),
            "interview_id": _CANDIDATE_TO_INTERVIEW.get(candidate.id),
        }
        for candidate in _CANDIDATES
    ]


def get_interview_report(interview_id: str) -> CandidateInterviewReport:
    interview = _INTERVIEWS.get(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    candidate = _CANDIDATES_BY_ID[interview.candidate_id]
    questions = _QUESTIONS.get(interview_id, [])
    replay_segments = _REPLAY_SEGMENTS.get(interview_id, [])
    return CandidateInterviewReport(
        candidate=candidate,
        interview=interview,
        questions=questions,
        replay_segments=replay_segments,
    )


def get_skill_analytics(interview_id: str) -> SkillAnalytics:
    analytics = _ANALYTICS.get(interview_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics


def compare_candidates() -> List[CandidateComparisonRow]:
    rows: List[CandidateComparisonRow] = []
    for interview in _INTERVIEWS.values():
        candidate = _CANDIDATES_BY_ID[interview.candidate_id]
        rows.append(
            CandidateComparisonRow(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                technical=interview.technical_score,
                communication=interview.communication_score,
                overall=interview.overall_score,
            )
        )
    return sorted(rows, key=lambda row: row.overall, reverse=True)
