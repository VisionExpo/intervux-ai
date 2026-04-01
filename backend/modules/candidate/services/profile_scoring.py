import json
import os
import time
from threading import Lock
from typing import List

from backend.models.candidate_portal import CandidateProfile
from backend.services.resume_parser_service import ParsedResume

SIGNUP_RATE_LIMIT_WINDOW_S = int(os.getenv("SIGNUP_RATE_LIMIT_WINDOW_S", "300"))
SIGNUP_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("SIGNUP_RATE_LIMIT_MAX_ATTEMPTS", "10"))
RESUME_RATE_LIMIT_WINDOW_S = int(os.getenv("RESUME_RATE_LIMIT_WINDOW_S", "60"))
RESUME_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv("RESUME_RATE_LIMIT_MAX_ATTEMPTS", "5"))

_signup_hits: dict[str, list[float]] = {}
_signup_lock = Lock()
_resume_hits: dict[str, list[float]] = {}
_resume_lock = Lock()


def allow_signup_attempt(ip: str) -> bool:
    now = time.time()
    window_start = now - SIGNUP_RATE_LIMIT_WINDOW_S
    with _signup_lock:
        attempts = [ts for ts in _signup_hits.get(ip, []) if ts >= window_start]
        if len(attempts) >= SIGNUP_RATE_LIMIT_MAX_ATTEMPTS:
            _signup_hits[ip] = attempts
            return False
        attempts.append(now)
        _signup_hits[ip] = attempts
        return True


def allow_resume_attempt(user_id: str) -> bool:
    now = time.time()
    window_start = now - RESUME_RATE_LIMIT_WINDOW_S
    with _resume_lock:
        attempts = [ts for ts in _resume_hits.get(user_id, []) if ts >= window_start]
        if len(attempts) >= RESUME_RATE_LIMIT_MAX_ATTEMPTS:
            _resume_hits[user_id] = attempts
            return False
        attempts.append(now)
        _resume_hits[user_id] = attempts
        return True


def calculate_profile_score(profile: CandidateProfile) -> float:
    score = 0.0

    if profile.name:
        score += 20

    if profile.skills:
        skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills
        score += min(len(skills) * 3, 30)

    if profile.experience_years:
        score += min(profile.experience_years * 2, 20)

    if profile.education:
        score += 15

    if profile.resume_url:
        score += 15

    return min(score, 100)


def calculate_resume_score(parsed: ParsedResume) -> tuple[float, List[str], List[str]]:
    score = 50.0
    strengths: List[str] = []
    weaknesses: List[str] = []

    if parsed.skills:
        score += min(len(parsed.skills) * 5, 25)
        strengths.append(f"{len(parsed.skills)} skills identified")

    if parsed.projects:
        score += min(len(parsed.projects) * 5, 15)
        strengths.append(f"{len(parsed.projects)} projects documented")

    if parsed.experience:
        score += 10
        strengths.append("Work experience present")
    else:
        weaknesses.append("No work experience mentioned")

    if parsed.education:
        score += 10
    else:
        weaknesses.append("Education details missing")

    return min(score, 100), strengths, weaknesses
