import traceback
import aiosqlite
from utils import DB_NAME
from ranking.faiss_index import FAISSIndex
from job_ingestion.pipeline import process_job
from job_ingestion.sources.linkedin import LinkedInSource
from job_ingestion.sources.indeed import IndeedSource
from job_ingestion.scheduler.source_scheduler import SourceScheduler
from playwright_stealth import stealth_async


async def process_queue(browser, context):
    

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
            await stealth_async(page)

            context_id = f"{source}_{job_id // 20}"

            try:

                await page.wait_for_timeout(1500)

                source_impl = SOURCES[source]

                data = await scheduler.run_enrich(
                    source_impl,
                    page,
                    url,
                    browser,
                    context_id
                )

                if isinstance(data, dict) and data.get("_reset_required"):
                    print("[SESSION] Purifying browser context...")

                    context = await scheduler.purify_context(browser, context)
                    scheduler.session_manager.reset(context_id)
                    await page.close()
                    continue

                if not data:
                    print(f"Skipping invalid {source} job: {url}")
                    scheduler.health.record_failure(context_id)
                    await page.close()
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

                scheduler.health.record_success(context_id)
                index.save()

            except Exception as e:

                print(f"Failed: {url} from {source}")

                print(traceback.format_exc())

                scheduler.health.record_failure(context_id)

            finally:
                if page:
                    await page.close()


    print("FAISS updated")