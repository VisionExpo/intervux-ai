import cv2
import numpy as np
from typing import Dict

from backend.config.setting import DEVICE


class EmotionAnalyzer:
    """
    Lightweight emotion & stress analyzer using facial cues.
    NOTE:
    This is NOT a clinical emotion detector.
    It estimates stress level from facial tension & movement.
    """

    def __init__(self):
        # Haar cascade is fast & reliable for real-time
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        print(f"[INFO] EmotionAnalyzer initialized on {DEVICE}")

    def analyze(self, frame: np.ndarray) -> Dict[str, float]:
        """
        Analyze a single video frame.
        Returns a stress score between 0.0 and 1.0
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60),
        )

        if len(faces) == 0:
            return {
                "stress_score": 0.0,
                "confidence": 0.5,
                "face_detected": False,
            }

        # Take the first detected face
        (x, y, w, h) = faces[0]
        face_roi = gray[y : y + h, x : x + w]

        # Heuristic: edge density → facial tension proxy
        edges = cv2.Canny(face_roi, 50, 150)
        edge_density = np.mean(edges > 0)

        # Normalize stress score
        stress_score = min(max(edge_density * 2.5, 0.0), 1.0)
        confidence = 1.0 - stress_score

        return {
            "stress_score": round(stress_score, 3),
            "confidence": round(confidence, 3),
            "face_detected": True,
        }
