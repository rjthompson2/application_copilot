import asyncio
from playwright.async_api import async_playwright
from ingestion.sources.wellfound import WellfoundSource


async def main():

    source = WellfoundSource()

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/Los_Angeles",
            extra_http_headers={
                "accept-language": "en-US,en;q=0.9",
            }
        )

        
        await context.add_init_script(
            """
            window.chrome = { runtime: {} };
            """
        )

        queries = [
            "software engineer"
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