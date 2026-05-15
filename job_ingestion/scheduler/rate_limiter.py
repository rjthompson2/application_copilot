import asyncio
import time
import random


class SourceRateLimiter:
    """
    Simple async rate limiter per source.
    """

    def __init__(self, min_interval_seconds: float = 5.0, jitter: float = 0.2):
        self.base_interval = min_interval_seconds
        self.current_interval = min_interval_seconds
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


    def update_from_failure_rate(self, failure_rate: float):
        """
        Adaptive tuning based on health.
        """

        # interval adaptation
        if failure_rate < 0.1:
            self.current_interval = max(1.0, self.base_interval * 0.7)

        elif failure_rate < 0.3:
            self.current_interval = self.base_interval

        elif failure_rate < 0.6:
            self.current_interval = self.base_interval * 1.5

        else:
            self.current_interval = self.base_interval * 2.5

        # jitter adaptation
        if failure_rate < 0.1:
            self.jitter = 0.1
        elif failure_rate < 0.3:
            self.jitter = 0.2
        else:
            self.jitter = 0.4

    def _interval_with_jitter(self):
        variation = self.current_interval * self.jitter

        return random.uniform(
            max(0, self.current_interval - variation),
            self.current_interval + variation
        )

    async def wait(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_called

            target = self._interval_with_jitter()

            if elapsed < target:
                await asyncio.sleep(target - elapsed)

            self.last_called = time.time()