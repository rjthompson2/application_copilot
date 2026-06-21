import traceback
import aiosqlite
from utils import DB_NAME
from ranking.faiss_index import get_or_build_index
from job_ingestion.pipeline import process_job
from job_ingestion.sources.linkedin import LinkedInSource
from job_ingestion.sources.indeed import IndeedSource
from job_ingestion.scheduler.source_scheduler import SourceScheduler
from playwright_stealth import stealth_async
import faiss
import asyncio
from playwright.async_api import async_playwright
from job_database.database import init_db
from job_ingestion.workers.discover_worker import run_discovery
from job_ingestion.workers.process_worker import process_queue
from config import SEARCH_QUERY, LOCATION
from utils import STORAGE_FILE, DB_NAME
from ranking.faiss_index import FAISSIndex


async def test_full_flow(client):
# async def process_queue(browser, context):

    # 1. INIT DATABASE
    await init_db()


    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            viewport={"width": 1366, "height": 768}
        )
    

        index =  FAISSIndex(dim=384)



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
                WHERE show=0
            """)

            list_jobs = await cursor.fetchall()
            assert len(list_jobs) > 1
            jobs = [list_jobs.pop(0)]

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

                    if not data:
                        jobs.append(list_jobs.pop(0))
                        await page.close()
                        continue
                    
                    assert data["description"] != ""


                    values = await process_job(
                        db=db,
                        index=index,
                        job_id=job_id,
                        old_hash=old_hash,
                        data=data,
                        db_save=False
                    )

                    assert type(values) == type({})


                except Exception as e:

                    print(f"Failed: {url} from {source}")

                    print(traceback.format_exc())

                    assert False


                finally:
                    if page:
                        await page.close()

