import asyncio
import time
import random


class SourceRateLimiter:
    """
    Simple async rate limiter per source.
    """

    def __init__(self, min_interval_seconds: float = 5.0, jitter: float = 0.2):
        self.min_interval = min_interval_seconds
        self.jitter = jitter
        self.last_called = 0
        self.lock = asyncio.Lock()

    def _compute_interval(self):
        # bounded variability
        variation = self.min_interval * self.jitter

        return random.uniform(
            max(0, self.min_interval - variation),
            self.min_interval + variation
        )

    async def wait(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_called

            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)

            self.last_called = time.time()