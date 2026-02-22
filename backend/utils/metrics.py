import time
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.request_counts = 0,
        self.error_count = 0,
        self.latencies = defaultdict(list)
        self.interviews_completed = 0

    def record_request(self):
        self.request_counts += 1

    def record_error(self):
        self.error_count += 1
    
    def record_latency(self, name: str, duration: float):
        self.latencies[name].append(duration)

    def record_interview_completed(self):
        self.interviews_completed += 1

    def snapshot(self):
        return {
            "request": self.request_counts,
            "error": self.error_count,
            "interviews_completed": self.interviews_completed,
            "avg_latency": {
                k: sum(v) / len(v) if v else 0
                for k, v in self.latencies.items()
            }
        }
    
Metrics = Metrics()