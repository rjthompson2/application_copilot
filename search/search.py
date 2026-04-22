import aiosqlite
import numpy as np
from ranking.embeddings import get_embedding
from ranking.faiss_index import build_faiss_index
from config import DB_NAME


async def search_jobs(resume_text: str, k=10):
    # 1. Embed resume
    resume_embedding = get_embedding(resume_text)

    # 2. Load FAISS index
    index = await build_faiss_index()

    # 3. Search
    results = index.search(resume_embedding, k=k)

    job_ids = [r["job_id"] for r in results]

    if not job_ids:
        return []

    # 4. Fetch jobs from DB
    placeholders = ",".join(["?"] * len(job_ids))

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            f"SELECT id, title FROM jobs WHERE id IN ({placeholders})",
            job_ids
        )
        results = await cursor.fetchall()

    return results