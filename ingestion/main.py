import asyncio
import aiosqlite
from playwright.async_api import async_playwright
from database.database import init_db, save_urls
from ingestion.linkedin_scraper import discover_jobs
from ingestion.process_queue import process_queue
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
            await process_queue(context)


        # 3. DISCOVER JOBS
        urls = await discover_jobs(
            context,
            query=SEARCH_QUERY,
            location=LOCATION
        )

        # 4. SAVE TO DB (queued)
        await save_urls(urls)

        # 5. ENRICH 
        await process_queue(context)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())