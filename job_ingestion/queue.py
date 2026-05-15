import aiosqlite
from utils import DB_NAME


async def enqueue_jobs(urls, source="linkedin"):

    async with aiosqlite.connect(DB_NAME) as db:

        for url in urls:

            await db.execute("""
                INSERT OR IGNORE INTO jobs (
                    url,
                    source,
                    status
                )
                VALUES (?, ?, 'queued')
            """, (
                url,
                source
            ))

        await db.commit()