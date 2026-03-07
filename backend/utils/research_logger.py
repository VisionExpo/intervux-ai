import hashlib
import json
import os
import threading
import time
from typing import Any, Dict


class ResearchLogger:
    def __init__(self):
        self.enabled = os.getenv("RESEARCH_LOG_ENABLED", "true").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self.file_path = os.getenv(
            "RESEARCH_LOG_PATH", "logs/research/evaluator_dataset.jsonl"
        )
        self._lock = threading.Lock()
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def _hash_answer(answer: str) -> str:
        clean = answer.strip().lower().encode("utf-8")
        return hashlib.sha256(clean).hexdigest()

    def write_evaluation_record(self, payload: Dict[str, Any]):
        if not self.enabled:
            return
        record = dict(payload)
        answer_text = ""
        if "answer" in record:
            answer_text = str(record.get("answer", ""))
        elif "answer_text" in record:
            answer_text = str(record.get("answer_text", ""))
        record["answer_hash"] = self._hash_answer(answer_text)
        record["timestamp"] = time.time()
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with self._lock:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line)


research_logger = ResearchLogger()
