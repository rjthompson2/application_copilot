from config import DB_NAME
from ingestion.enrichment import enrich_job
from ranking.cache import encode_and_cache
from ranking.faiss_index import FAISSIndex
import numpy as np
import aiosqlite

async def process_queue(context):
    # Load FAISS index once
    index = FAISSIndex.load()

    # process jobs
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, url, embedding_text_hash FROM jobs WHERE status='queued'"
        )
        jobs = await cursor.fetchall()

        print(f"Processing {len(jobs)} jobs")

        page = await context.new_page()

        for job_id, url, old_hash in jobs:
            try:
                await page.wait_for_timeout(2000)

                # Get data for each job
                data = await enrich_job(page, url)
                if not data:
                    continue

                job_text = f"""
                {data.get("title", "")}
                {data.get("company", "")}
                {data.get("location", "")}
                {data.get("description", "")}
                """

                # caching to prevent duplication
                embedding, new_hash = encode_and_cache(job_text, old_hash)

                emb_blob = None
                if embedding is not None:
                    emb_blob = embedding.astype("float32").tobytes()

                # NORMALIZE (important for FAISS)
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm

                    # ADD TO FAISS
                    index.add(job_id, embedding)

                # add all values into database
                await db.execute("""
                    UPDATE jobs
                    SET title=?, company=?, location=?, description=?,
                        skills=?, seniority=?, status='done',
                        embedding=?, embedding_text_hash=?
                    WHERE id=?
                """, (
                    data["title"],
                    data["company"],
                    data["location"],
                    data["description"],
                    data["skills"],
                    data["seniority"],
                    emb_blob,
                    new_hash,
                    job_id
                ))

                await db.commit()

                print("Processed:", data["title"])

            except Exception as e:
                print("Failed:", url, e)
    
    index.save()
    print("FAISS index updated")