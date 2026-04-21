import asyncio
from playwright.async_api import async_playwright
from database.database import init_db, save_urls
from ingestion.scraper import discover_jobs
from ingestion.process_queue import process_queue
from resume.resume import load_resume, build_user_profile
from resume.ui import load_resume_interactive
from config import SEARCH_QUERY, LOCATION, STORAGE_FILE, RESUME_FILE

async def main():
    # 1. INIT DATABASE
    await init_db()

    # 2. BUILD USER PROFILE

    resume_text = load_resume_interactive()
    profile = build_user_profile(resume_text)

    print("Profile loaded:")
    print(profile)

    # 3. DISCOVER JOBS
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # load saved login session if exists
        context = await browser.new_context(storage_state=STORAGE_FILE)

        urls = await discover_jobs(
            context,
            query=SEARCH_QUERY,
            location=LOCATION
        )
        print(f"Discovered {len(urls)} jobs")

        # 4. SAVE TO DB (queued)
        await save_urls(urls)

        # 5. ENRICH + SCORE + FILTER
        await process_queue(context, profile)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())