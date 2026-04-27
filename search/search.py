import aiosqlite
import numpy as np
from ranking.embeddings import get_embedding
from ranking.faiss_index import FAISSIndex
from ranking.scoring import compute_resume_score
from config import DB_NAME


async def search_jobs(resume_text: str, profile, k=10):
    # 1. Embed resume
    resume_embedding = get_embedding(resume_text)

    # normalize
    norm = np.linalg.norm(resume_embedding)
    if norm > 0:
        resume_embedding = resume_embedding / norm

    # 2. Load FAISS index
    index = FAISSIndex.load()

    # 3. Search
    results = index.search(resume_embedding, k=k)

    job_ids = [r["job_id"] for r in results]
    faiss_scores = [r["faiss_score"] for r in results]

    if not job_ids:
        return []

    # 4. Fetch jobs from DB
    placeholders = ",".join(["?"] * len(job_ids))

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            f"SELECT id, title, company, location, skills, seniority FROM jobs WHERE id IN ({placeholders})",
            job_ids
        )
        results = await cursor.fetchall()
        
    # map jobs
    job_map = {row[0]: {
        "id": row[0],
        "title": row[1],
        "company": row[2],
        "location": row[3],
        "skills": row[4],
        "seniority": row[5]
    } for row in results}

    # 5. Apply hybrid scoring
    final_results = []

    for i, row in enumerate(results):
        job = {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "skills": row[4] if len(row) > 4 else "",
        }

        final_score, skill_score = compute_resume_score(
            job,
            profile,
            faiss_scores[i]
        )

        job["score"] = final_score
        job["faiss_score"] = faiss_scores[i]
        job["skill_score"] = skill_score

        final_results.append(job)

    # sort by final score
    final_results.sort(key=lambda x: x["score"], reverse=True)

    return final_results