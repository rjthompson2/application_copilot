from urllib.parse import quote


class WellfoundSource:

    name = "wellfound"

    async def discover(self, context, query, location=None):

        page = await context.new_page()

        await page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        )

        url = f"https://wellfound.com/jobs?query={query}"

        print(f"[Wellfound] Visiting: {url}")

        await page.goto(url, wait_until="domcontentloaded")

        # let JS render job cards
        await page.wait_for_timeout(5000)

        # scroll a bit to trigger lazy loading
        for _ in range(3):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1500)

        # extract job links
        links = await page.eval_on_selector_all(
            "a",
            """
            els => els
                .map(e => e.href)
                .filter(h =>
                    h &&
                    h.includes('/jobs/') &&
                    !h.includes('companies')
                )
            """
        )

        # normalize + dedupe
        cleaned = set()

        for link in links:
            cleaned.add(link.split("?")[0])

        cleaned = list(cleaned)

        print(f"[Wellfound] Found {len(cleaned)} jobs")

        await page.close()

        return cleaned


    async def enrich(self, page, url):
        """
        NOT USED in aggregation layer
        kept for interface compatibility
        """

        return None