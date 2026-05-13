import asyncio

from playwright.async_api import async_playwright

from ingestion.workers.process_worker import process_queue


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        context = await p.chromium.launch_persistent_context(
            user_data_dir="./browser_profile",
            headless=False
        )

        await process_queue(context)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())