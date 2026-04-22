import aiosqlite
from config import DB_NAME

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
            await db.execute(
                "INSERT OR IGNORE INTO jobs (url, status, source) VALUES (?, 'queued', 'linkedin')",
                (url,)
            )

        await db.commit()