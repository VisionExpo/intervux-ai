from typing import List, Dict


class VisemeService:
    """
    Generates basic viseme timing metadata for avatar lip-sync.
    NOTE:
    This is duration-based, not phoneme-accurate.
    Designed for low-latency real-time avatars.
    """

    def generate(
        self,
        audio_duration_ms: int,
        frame_interval_ms: int = 120,
    ) -> List[Dict[str, int]]:
        """
        Generate a simple viseme timeline.

        Returns a list of:
        {
            "time_ms": int,
            "mouth_open": int  # 0 or 1
        }
        """

        visemes = []
        time_ms = 0
        open_state = 1

        while time_ms < audio_duration_ms:
            visemes.append({
                "time_ms": time_ms,
                "mouth_open": open_state,
            })

            # Alternate open / close
            open_state = 1 - open_state
            time_ms += frame_interval_ms

        return visemes
