import asyncio
import aiosqlite
from playwright.async_api import async_playwright
from job_database.database import init_db
from job_ingestion.workers.discover_worker import run_discovery
from job_ingestion.workers.process_worker import process_queue
from config import SEARCH_QUERY, LOCATION
from utils import STORAGE_FILE, DB_NAME


async def main():
    # 1. INIT DATABASE
    await init_db()


    async with async_playwright() as p:
        browser = await p.chromium.launch()

        context = await browser.new_context(
            viewport={"width": 1366, "height": 768}
        )


        # 2. CHECK IF JOBS ALREADY IN DB
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                "SELECT id FROM jobs WHERE status='queued'"
            )
            jobs = await cursor.fetchall()
            if len(jobs) > 0:
                print("Processing jobs in queue...")
                await process_queue(browser, context)
        
        # 3. DISCOVERAND QUEUE JOBS
        await run_discovery(
            context,
            query=SEARCH_QUERY,
            location=LOCATION
        )

        # 4. ENRICH 
        await process_queue(browser, context)
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())