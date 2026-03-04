class DifficultyCalibrationEngine:
    def __init__(self, start_level=2):
        self.level = max(1, min(3, int(start_level)))
        self.strong_streak = 0
        self.weak_streak = 0

    def update(self, score, confidence):
        try:
            score_value = float(score)
        except Exception:
            score_value = 0.0

        try:
            confidence_value = float(confidence)
        except Exception:
            confidence_value = 0.0

        if confidence_value < 0.4:
            self.strong_streak = 0
            self.weak_streak = 0
            return self.level

        if score_value >= 8:
            self.strong_streak += 1
            self.weak_streak = 0
            if self.strong_streak >= 2:
                self.level += 1
                self.strong_streak = 0
        elif score_value <= 4:
            self.weak_streak += 1
            self.strong_streak = 0
            if self.weak_streak >= 2:
                self.level -= 1
                self.weak_streak = 0
        else:
            self.strong_streak = 0
            self.weak_streak = 0

        self.level = max(1, min(3, self.level))
        return self.level
