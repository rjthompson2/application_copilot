import aiosqlite
from utils import DB_NAME
from job_ingestion.utils import normalize_url
import asyncio

CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    skills TEXT,
    seniority TEXT,
    source TEXT,
    score REAL,
    embedding_score REAL,
    status TEXT DEFAULT 'queued',
    show BOOLEAN DEFAULT 1,
    embedding BLOB,
    embedding_text_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_TABLE_QUERY)
        await db.commit()


async def insert_job(job):
    query = """
    INSERT OR IGNORE INTO jobs (title, company, location, url, description, skills, seniority, source)
    VALUES (?, ?, ?, ?, '', '', '', ?)
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, (
            job["title"],
            job["company"],
            job["location"],
            job["url"],
            job["source"]
        ))
        await db.commit()


async def get_jobs_without_details():
    query = """
    SELECT id, url FROM jobs
    WHERE description IS NULL OR description = ''
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        return await cursor.fetchall()


async def get_jobs():
    query = """
    SELECT id, title, company, location, show, status FROM jobs;
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        return await cursor.fetchall()


async def get_history():
    query = """
    SELECT id, title, company, location, description FROM jobs WHERE status='saved';
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)
        return await cursor.fetchall()


async def get_title(job_id):
    query = """
    SELECT company, title FROM jobs
    WHERE id = ?
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query, (job_id,))
        return await cursor.fetchall()


async def update_job(job_id, description, skills, seniority):
    query = """
    UPDATE jobs
    SET description = ?, skills = ?, seniority = ?
    WHERE id = ?
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, (description, skills, seniority, job_id))
        await db.commit()


async def save_urls(urls):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                skills TEXT,
                seniority TEXT,
                score REAL,
                embedding_score REAL,
                embedding BLOB,
                embedding_text_hash TEXT,
                status TEXT DEFAULT 'queued',
                source TEXT
            )
        """)

        for url in urls:
            url = normalize_url(url)
            await db.execute(
                "INSERT OR IGNORE INTO jobs (url, status, source) VALUES (?, 'queued', 'linkedin')",
                (url,)
            )

        await db.commit()



async def get_metrics():
    query = """
    SELECT id, title, company, location, show, status FROM jobs WHERE status='saved';
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)

        applied = await cursor.fetchall()

    
    query = """
    SELECT id, title, company, location, show, status FROM jobs WHERE status='done' AND show=0;
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)

        failed = await cursor.fetchall()

    
    query = """
    SELECT id, title, company, location, show, status FROM jobs WHERE show=0;
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)

        total = await cursor.fetchall()
    
    return applied, failed, total

async def delete_source(source):
    query = """
        DELETE FROM jobs
        WHERE source = ? AND status='queued'
    """
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query, (
            source,
        ))
        await db.commit()


async def show_all():
    query = """
        SELECT url, embedding, status, show, skills FROM jobs WHERE status='done';
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query)

        all_jobs = await cursor.fetchall()
        return all_jobs


# Clean testing data from db
async def clean_db():
    query = """
        DELETE FROM jobs
        WHERE source = 'TEST';
    """

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query)
        await db.commit()


if __name__ == "__main__":
    # asyncio.run(clean_db())
    all_jobs = asyncio.run(show_all())
    for job in all_jobs:
        embedding = "None"
        try:
            embedding = job[1][:10]
        except:
            pass
        display = f"{job[0]}\n{embedding} | {job[2]} | {str(bool(job[3]))}\n"
        print(display)