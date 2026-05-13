import asyncio
from playwright.async_api import async_playwright
from ingestion.sources.indeed import IndeedSource


async def main():

    source = IndeedSource()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context()

        queries = [
            "software engineer",
        ]

        for q in queries:

            print(f"\n=== QUERY: {q} ===")

            jobs = await source.discover(context, q)

            print(f"Found {len(jobs)} jobs")

            for job in jobs[:10]:
                print(job)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())