from typing import Dict, List


class SkillCoverageEngine:
    def __init__(self, skills: List[str]):
        deduped = []
        seen = set()
        for skill in skills:
            if not isinstance(skill, str):
                continue
            value = skill.strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)

        self.skills: Dict[str, int] = {skill: 0 for skill in deduped}
        self.total_questions = 0

    def update(self, skill: str):
        if skill in self.skills:
            self.skills[skill] += 1
        self.total_questions += 1

    def next_skill(self) -> str:
        if not self.skills:
            return "Machine Learning"
        return min(self.skills, key=self.skills.get)

    def snapshot(self) -> Dict[str, int]:
        return dict(self.skills)

    def meets_minimum(self, min_questions_per_skill: int) -> bool:
        if not self.skills:
            return True
        threshold = max(0, int(min_questions_per_skill))
        return all(count >= threshold for count in self.skills.values())
