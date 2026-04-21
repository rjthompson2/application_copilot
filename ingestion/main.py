import asyncio
from playwright.async_api import async_playwright
from application_copilot.config import STORAGE_FILE
from application_copilot.ingestion.scraper import discover_jobs
from application_copilot.database.database import save_urls
from application_copilot.ingestion.process_queue import process_queue


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(storage_state="auth.json")

        # 1. DISCOVER
        urls = await discover_jobs(
            context,
            "backend engineer",
            "United States"
        )

        await save_urls(urls)

        # 2. ENRICH
        await process_queue(context)

        await browser.close()
        

if __name__ == "__main__":
    asyncio.run(main())