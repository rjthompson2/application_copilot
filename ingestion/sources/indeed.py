
from ingestion.enrichment import enrich_job
from ingestion.sources.base import JobSource

class IndeedSource(JobSource):

    name = "indeed"

    async def discover(self, context, query, location="remote"):

        page = await context.new_page()

        url = (
            "https://www.indeed.com/jobs"
            f"?q={query}"
            f"&l={location}"
        )

        print(f"[Indeed] Visiting: {url}")

        await page.goto(url, wait_until="domcontentloaded")

        await page.wait_for_timeout(4000)

        # scroll to force job cards to render
        for _ in range(4):
            await page.mouse.wheel(0, 2500)
            await page.wait_for_timeout(1500)

        # extract job keys, NOT URLs
        job_keys = await page.evaluate("""
        () => {
            const cards = document.querySelectorAll('[data-jk]');
            return Array.from(cards)
                .map(c => c.getAttribute('data-jk'))
                .filter(Boolean);
        }
        """)

        # convert to stable URLs
        links = [
            f"https://www.indeed.com/viewjob?jk={jk}"
            for jk in job_keys
        ]

        print(f"[Indeed] Found {len(links)} jobs")

        await page.close()

        return list(set(links))

    async def enrich(self, page, url):
        if not await self.is_valid_indeed_page(page):
            print("Invalid page")
            return None
        
        if not await self.is_not_cloudflare(page):
            print("BLOCKED via cloudflare")
            return None
        
        return await enrich_job(page, url)
    

    async def is_valid_indeed_page(self, page):

        content = await page.content()

        if "doesn't exist" in content.lower():
            return False

        if "not available right now" in content.lower():
            return False

        if "we can't find this" in content.lower():
            return False
        
        if "this job has expired" in content.lower():
            return False

        return True
    
    async def is_not_cloudflare(self, page):
        content = await page.content()

        if "cloudflare pages analytics" in content.lower():
            return False
        
        if "additional verification" in content.lower():
            return False
        
        required_selectors = [
            "h1",
            "[data-testid='jobsearch-JobInfoHeader-title']",
            ".jobsearch-JobInfoHeader-title"
        ]

        has_any_title = False
        for sel in required_selectors:
            try:
                if await page.locator(sel).count() > 0:
                    has_any_title = True
                    break
            except:
                continue

        return has_any_title