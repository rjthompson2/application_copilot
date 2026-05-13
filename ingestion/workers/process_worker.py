import traceback
import aiosqlite
from utils import DB_NAME
from ranking.faiss_index import FAISSIndex
from ingestion.pipeline import process_job
from ingestion.sources.linkedin import LinkedInSource
from ingestion.sources.indeed import IndeedSource
from ingestion.scheduler.source_scheduler import SourceScheduler


async def process_queue(context):

    index = FAISSIndex.load()



    SOURCES = {
        "linkedin": LinkedInSource(),
        "indeed": IndeedSource()
    }



    scheduler = SourceScheduler()

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT
                id,
                url,
                source,
                embedding_text_hash
            FROM jobs
            WHERE status='queued'
        """)

        jobs = await cursor.fetchall()

        print(f"Processing {len(jobs)} jobs")

        for job_id, url, source, old_hash in jobs:

            page = await context.new_page()

            try:

                await page.wait_for_timeout(1500)

                source_impl = SOURCES[source]

                data = await scheduler.run_enrich(
                    source_impl,
                    page,
                    url
                )

                if not data:
                    print(f"Skipping invalid {source} job: {url}")
                    scheduler.health.record_failure(source)
                    continue
                


                await process_job(
                    db=db,
                    index=index,
                    job_id=job_id,
                    old_hash=old_hash,
                    data=data
                )

                print(
                    f"Processed: {data['title']} from {source}"
                )

                scheduler.health.record_success(source)

            except Exception as e:

                print(f"Failed: {url} from {source}")

                print(traceback.format_exc())

                scheduler.health.record_failure(source)

        await page.close()

    index.save()

    print("FAISS updated")