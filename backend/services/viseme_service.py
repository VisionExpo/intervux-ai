from typing import List, Dict


class VisemeService:
    """
    Generates basic viseme timing metadata for avatar lip-sync.
    NOTE:
    This is duration-based, not phoneme-accurate.
    Designed for low-latency real-time avatars.
    """

    def generate_timeline(
        self,
        audio_duration_ms: int,
        frame_interval_ms: int = 120,
    ) -> List[Dict[str, int]]:
        """
        Generate a lightweight viseme timeline for browser lip-sync.

        Returns a list of:
        {
            "start": int,
            "end": int,
            "viseme": int
        }
        """

        if audio_duration_ms <= 0:
            return []

        viseme_cycle = [1, 3, 2, 4, 0]
        idx = 0
        visemes: List[Dict[str, int]] = []
        start = 0

        while start < audio_duration_ms:
            end = min(start + frame_interval_ms, audio_duration_ms)
            visemes.append(
                {
                    "start": start,
                    "end": end,
                    "viseme": viseme_cycle[idx % len(viseme_cycle)],
                }
            )
            idx += 1
            start = end

        return visemes
