import time
from collections import defaultdict


class SourceHealthTracker:

    def __init__(self):
        self.success = defaultdict(int)
        self.failure = defaultdict(int)

    def record_success(self, source_name: str):
        self.success[source_name] += 1

    def record_failure(self, source_name: str):
        self.failure[source_name] += 1

    def failure_rate(self, source_name: str) -> float:
        s = self.success[source_name]
        f = self.failure[source_name]

        total = s + f
        if total == 0:
            return 0.0

        return f / total