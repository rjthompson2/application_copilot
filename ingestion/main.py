import asyncio
import aiosqlite
from playwright.async_api import async_playwright
from database.database import init_db
from ingestion.workers.discover_worker import run_discovery
from ingestion.workers.process_worker import process_queue
from config import SEARCH_QUERY, LOCATION
from utils import STORAGE_FILE, DB_NAME

async def main():
    # 1. INIT DATABASE
    await init_db()


    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # load saved login session if exists
        context = await browser.new_context(storage_state=STORAGE_FILE)


        # 2. CHECK IF JOBS ALREADY IN DB
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(
                "SELECT id, url, embedding_text_hash FROM jobs WHERE status='queued'"
            )
            jobs = await cursor.fetchall()
            if len(jobs) > 0:
                print("Processing jobs in queue...")
                await process_queue(context)


        # 3. DISCOVERAND QUEUE JOBS
        await run_discovery(
            context,
            query=SEARCH_QUERY,
            location=LOCATION
        )

        # 4. ENRICH 
        await process_queue(context)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())