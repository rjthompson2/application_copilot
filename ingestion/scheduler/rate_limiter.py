import asyncio
import time


class SourceRateLimiter:
    """
    Simple async rate limiter per source.
    """

    def __init__(self, min_interval_seconds: float = 5.0):
        self.min_interval = min_interval_seconds
        self.last_called = 0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_called

            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                await asyncio.sleep(wait_time)

            self.last_called = time.time()