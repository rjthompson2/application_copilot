from typing import List, Dict
from playwright.async_api import async_playwright
import urllib.parse
import time


class LinkedInProvider:
    async def search_people(self, company: str, role: str) -> List[Dict]:
        raise NotImplementedError


class GoogleLinkedInProvider:
    async def search_people(self, company: str, role: str):

        queries = {
            "technical recruiter": f"{company} technical recruiter linkedin",
            "engineering manager": f"{company} engineering manager {role} linkedin",
            "talent acquisition": f"{company} talent acquisition linkedin"
        }

        results = []

        for title, q in queries.items():

            encoded = urllib.parse.quote(q)

            url = f"https://www.google.com/search?q={encoded}"

            results.append({
                "title": title,
                "company": company,
                "query": q,
                "search_url": url
            })

        return results
    


class PlaywrightLinkedInProvider:
    async def search_people(self, company: str, role: str):

        queries = {
            "technical recruiter": f"{company} technical recruiter linkedin",
            "engineering manager": f"{company} engineering manager {role} linkedin",
            "talent acquisition": f"{company} talent acquisition linkedin"
        }

        output = []
        browser = None

        try:

            async with async_playwright() as p:

                browser = await p.chromium.launch(headless=False)
                print("Launching Playwright...")

                context = await browser.new_context(
                    viewport={"width": 1366, "height": 768}
                )

                page = await context.new_page()


                for q, query in queries.items():
                    url = (
                        "https://www.duckduckgo.com/?q="
                        + query.replace(" ", "+")
                    )
                    print("Navigating to:", url)

                    await page.goto(
                        url,
                        wait_until="load"
                    )
                    await page.wait_for_selector("h2", timeout=10000)
                    print("Page Loaded.")

                    results = await page.query_selector_all(
                        'div > h2 > a[href*="linkedin.com"]'
                    )
                    print("Results Found.")

                    for r in results[:5]:

                        text = await r.inner_text()
                        href = await r.get_attribute("href")

                        output.append({
                            "company": company,
                            "query": q,
                            "title": str(text),
                            "search_url": str(href),
                            "source": "duckduckgo"
                        })
                    
                await browser.close()
            return output

        except Exception as e:
                if browser:
                    await browser.close()
                print("ERROR IN PLAYWRIGHT:", repr(e))

                return []
    
    def parse_text(self, text):
        print(text)

