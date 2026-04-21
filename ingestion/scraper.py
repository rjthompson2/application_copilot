import asyncio
from playwright.async_api import async_playwright
from config import SEARCH_QUERY, LOCATION, MAX_PAGES, LINKEDIN_URL
from database.database import insert_job
from ingestion.utils import human_delay


async def discover_jobs(context, query, location):
    page = await context.new_page()

    url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={query}&location={location}&start=0"
    )

    await page.goto(url, wait_until="commit", timeout=90000)
    await page.wait_for_timeout(5000)

    # extract URLs only (no DOM dependency)
    links = await page.locator("a").evaluate_all("""
        els => els
            .map(e => e.href)
            .filter(h => h && h.includes('/jobs/view/'))
    """)

    links = list(set(links))

    print(f"Discovered {len(links)} jobs")

    return links

async def extract_title(page):
    # 1. Try DOM
    try:
        title = await page.locator("h1").first.text_content(timeout=3000)
        if title:
            return title.strip()
    except:
        pass

    # 2. Meta fallback (YOU ARE HERE MOST OF THE TIME NOW)
    try:
        title = await page.title()
        if title:
            return title.strip()
    except:
        pass

    # 3. URL fallback
    try:
        slug = page.url.split("/jobs/view/")[-1].split("/")[0]
        return slug.replace("-", " ")
    except:
        return ""

async def extract_company(page):
    candidates = [
        "a.topcard__org-name-link",
        "span.topcard__flavor",
        ".job-details-jobs-unified-top-card__company-name"
    ]

    for sel in candidates:
        try:
            text = await page.locator(sel).first.text_content(timeout=3000)
            if text:
                return text.strip()
        except:
            continue

    return ""