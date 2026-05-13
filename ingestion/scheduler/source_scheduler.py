import asyncio
from ingestion.scheduler.rate_limiter import SourceRateLimiter


class SourceScheduler:

    def __init__(self):
        self.limiters = {}
        self.semaphores = {}

        # default per-source pacing (tune later)
        self.default_interval = {
            "linkedin": 0.0,
            "indeed": 1.44,
        }
        # concurrency limits per source
        self.default_concurrency = {
            "linkedin": 2,
            "indeed": 1
        }

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

        if source_name not in self.limiters:
            self.limiters[source_name] = SourceRateLimiter(interval)

        return self.limiters[source_name]

    async def run_discover(self, source, context, query, location):
        limiter = self.get_limiter(source.name)
        semaphore = self.get_semaphore(source.name)

        await limiter.wait()

        async with semaphore:
            return await source.discover(context, query, location)

    async def run_enrich(self, source, page, url):
        limiter = self.get_limiter(source.name)
        semaphore = self.get_semaphore(source.name)

        await limiter.wait()

        async with semaphore:
            return await source.enrich(page, url)