from ingestion.sources.base import JobSource
from config import MAX_PAGES
from ingestion.enrichment import enrich_job


class LinkedInSource(JobSource):

    name = "linkedin"

    async def discover(self, context, query, location):

        page = await context.new_page()

        all_links = set()
        start = 0

        for p in range(MAX_PAGES):

            url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={query}"
                f"&location={location}"
                f"&start={start}"
            )

            print(f"[LinkedIn] Page {p+1}: {url}")

            await page.goto(
                url,
                wait_until="domcontentloaded"
            )

            try:
                await page.wait_for_selector(
                    "a[href*='/jobs/view']",
                    timeout=10000
                )

            except:
                print("No job links found")
                break

            links = await page.eval_on_selector_all(
                "a[href*='/jobs/view']",
                "els => els.map(e => e.href)"
            )

            links = {
                link.split("?")[0]
                for link in links
                if link and "/jobs/view" in link
            }

            before = len(all_links)

            all_links.update(links)

            after = len(all_links)

            print(
                f"[LinkedIn] Found {len(links)} links "
                f"(total={after})"
            )

            if after == before:
                print("No new jobs → stopping")
                break

            start += 25

        await page.close()

        return list(all_links)

    async def enrich(self, page, url):

        return await enrich_job(page, url)