import asyncio

from playwright.async_api import async_playwright

from ingestion.workers.discover_worker import run_discovery
from config import SEARCH_QUERY, LOCATION
from utils import STORAGE_FILE


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        context = await browser.new_context(storage_state=STORAGE_FILE)

        await run_discovery(
            context=context,
            query=SEARCH_QUERY,
            location=LOCATION
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())