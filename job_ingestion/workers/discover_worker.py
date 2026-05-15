from job_ingestion.sources.linkedin import LinkedInSource
from job_ingestion.sources.indeed import IndeedSource
from job_ingestion.queue import enqueue_jobs


async def run_discovery(
    context,
    query,
    location
):

    sources = [
        LinkedInSource(),
        # IndeedSource()
    ]
    for source in sources:
        urls = await source.discover(
            context,
            query,
            location
        )

        await enqueue_jobs(
            urls,
            source=source.name
        )

        print(f"Queued {len(urls)} jobs from {source.name}")