import asyncio
from job_ingestion.scheduler.rate_limiter import SourceRateLimiter
from job_ingestion.scheduler.source_health import SourceHealthTracker
import time
import random


class SourceScheduler:

    def __init__(self):
        self.limiters = {}
        self.semaphores = {}

        # default per-source pacing (tune later)
        self.default_interval = {
            "linkedin": 0.0,
            "indeed": 5.44,
        }
        # additional jittering to prevent identical behavior
        self.default_jitter = {
            "linkedin": 0.1,
            "indeed": 0.3
        }
        # concurrency limits per source
        self.default_concurrency = {
            "linkedin": 2,
            "indeed": 1
        }

        self.health = SourceHealthTracker()
        self.session_manager = SessionManager()

    def get_semaphore(self, source_name: str):

        if source_name not in self.semaphores:

            limit = self.default_concurrency.get(
                source_name,
                1
            )

            self.semaphores[source_name] = asyncio.Semaphore(limit)

        return self.semaphores[source_name]

    def get_limiter(self, source_name: str):
        interval = self.default_interval.get(source_name, 6.0)
        jitter = self.default_jitter.get(source_name, 0.2)

        if source_name not in self.limiters:
            self.limiters[source_name] = SourceRateLimiter(
                interval,
                jitter=jitter
        )

        limiter = self.limiters[source_name]


        failure_rate = self.health.failure_rate(source_name)
        limiter.update_from_failure_rate(failure_rate)
        return limiter

    async def run_discover(self, source, context, query, location):
        limiter = self.get_limiter(source.name)
        semaphore = self.get_semaphore(source.name)

        await limiter.wait()

        async with semaphore:
            return await source.discover(context, query, location)

    async def run_enrich(self, source, page, url, browser=None, context_id=None):
        limiter = self.get_limiter(source.name)
        semaphore = self.get_semaphore(source.name)

        await limiter.wait()

        async with semaphore:

            result = await source.enrich(page, url)

            # session tracking hooks
            if context_id:
                if result:
                    self.session_manager.record_success(context_id)
                else:
                    self.session_manager.record_failure(context_id)

                if self.session_manager.should_reset(context_id) and browser is not None:
                    return {"_reset_required": True}

            return result
        

    def update_from_failure_rate(self, failure_rate: float):
        """
        Adaptive tuning:
        - more failures → slower + more jitter
        - fewer failures → faster + less jitter
        """

        # interval scaling
        if failure_rate < 0.1:
            self.current_interval = max(1.0, self.base_interval * 0.7)

        elif failure_rate < 0.3:
            self.current_interval = self.base_interval

        elif failure_rate < 0.6:
            self.current_interval = self.base_interval * 1.5

        else:
            self.current_interval = self.base_interval * 2.5

        # jitter scaling
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

    async def purify_context(self, browser, old_context):
        """
        Fully resets browser session state.
        """

        try:
            await old_context.close()
        except:
            pass
        
        new_context = await browser.new_context()

        return new_context



class SessionManager:

    def __init__(self):
        self.context_usage = {}
        self.context_failures = {}

        self.max_usage = 20          # jobs per context
        self.max_failures = 5        # failures before reset

    def register_context(self, context_id: str):
        if context_id not in self.context_usage:
            self.context_usage[context_id] = 0
            self.context_failures[context_id] = 0

    def record_success(self, context_id: str):
        if context_id not in self.context_usage:
            self.context_usage[context_id] = 0
            self.context_failures[context_id] = 0

        self.context_usage[context_id] += 1

    def record_failure(self, context_id: str):
        if context_id not in self.context_usage:
            self.context_usage[context_id] = 0
            self.context_failures[context_id] = 0

        self.context_usage[context_id] += 1
        self.context_failures[context_id] += 1

    def should_reset(self, context_id: str) -> bool:
        return (
            self.context_usage.get(context_id, 0) >= self.max_usage
            or self.context_failures.get(context_id, 0) >= self.max_failures
        )

    def reset(self, context_id: str):
        self.context_usage[context_id] = 0
        self.context_failures[context_id] = 0