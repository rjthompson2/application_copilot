import asyncio
from playwright.async_api import async_playwright
from database.database import init_db, save_urls
from ingestion.linkedin_scraper import discover_jobs
from ingestion.process_queue import process_queue
from config import SEARCH_QUERY, LOCATION
from utils import STORAGE_FILE

async def main():
    # 1. INIT DATABASE
    await init_db()

    # 3. DISCOVER JOBS
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # load saved login session if exists
        context = await browser.new_context(storage_state=STORAGE_FILE)

        urls = await discover_jobs(
            context,
            query=SEARCH_QUERY,
            location=LOCATION
        )
        print(f"Discovered {len(urls)} jobs")

        # 4. SAVE TO DB (queued)
        await save_urls(urls)

        # 5. ENRICH 
        await process_queue(context)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())