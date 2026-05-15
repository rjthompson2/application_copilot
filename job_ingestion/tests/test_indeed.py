import asyncio
from playwright.async_api import async_playwright
from job_ingestion.sources.indeed import IndeedSource


async def main():

    source = IndeedSource()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            # viewport={"width": 1366, "height": 768},
            # user_agent=(
            #     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            #     "AppleWebKit/537.36 (KHTML, like Gecko) "
            #     "Chrome/122.0.0.0 Safari/537.36"
            # ),
        )

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