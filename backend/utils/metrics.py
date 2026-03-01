import time
from collections import defaultdict
from threading import Lock

class Metrics:
    def __init__(self):
        self._lock = Lock()
        self.request_counts = 0
        self.error_count = 0
        self.latencies = defaultdict(list)
        self.interviews_completed = 0
        self.gauges = {}
        self.counters = defaultdict(int)

    def record_request(self):
        with self._lock:
            self.request_counts += 1

    def record_error(self):
        with self._lock:
            self.error_count += 1
    
    def record_latency(self, name: str, duration: float):
        with self._lock:
            self.latencies[name].append(duration)

    def record_interview_completed(self):
        with self._lock:
            self.interviews_completed += 1

    def record_gauge(self, name: str, value: float):
        with self._lock:
            self.gauges[name] = value

    def increment_counter(self, name: str, value: int = 1):
        with self._lock:
            self.counters[name] += value

    def recent_latency(self, name: str, default: float = 0.0) -> float:
        with self._lock:
            values = self.latencies.get(name, [])
            return values[-1] if values else default

    def snapshot(self):
        with self._lock:
            return {
                "request": self.request_counts,
                "error": self.error_count,
                "interviews_completed": self.interviews_completed,
                "avg_latency": {
                    k: sum(v) / len(v) if v else 0
                    for k, v in self.latencies.items()
                },
                "gauges": dict(self.gauges),
                "counters": dict(self.counters),
            }
    
metrics = Metrics()
