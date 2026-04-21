from config import DB_NAME
from ingestion.enrichment import enrich_job
from ranking.scoring import score_job, MIN_SCORE
import aiosqlite

async def process_queue(context, profile):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, url FROM jobs WHERE status='queued'"
        )
        jobs = await cursor.fetchall()

    print(f"Enriching {len(jobs)} jobs")

    page = await context.new_page()

    for job_id, url in jobs:
        try:
            await page.wait_for_timeout(2000)  # important throttling fix

            data = await enrich_job(page, url)

            if not data:
                continue

            score = score_job(data, profile)
            if score < MIN_SCORE:
                print("Skipping low-score job:", data["title"], score)
                continue

            data["score"] = score

            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("""
                    UPDATE jobs
                    SET title=?, company=?, location=?, description=?,
                        skills=?, seniority=?, status='done', score=?
                    WHERE id=?
                """, (
                    data["title"],
                    data["company"],
                    data["location"],
                    data["description"],
                    data["skills"],
                    data["seniority"],
                    score,
                    job_id
                ))
                await db.commit()

            print("Title:", data["title"])

        except Exception as e:
            print("Failed:", url, e)