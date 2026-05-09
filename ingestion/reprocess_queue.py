from utils import DB_NAME
from ingestion.enrichment import enrich_job
from ranking.cache import encode_and_cache
from ranking.faiss_index import FAISSIndex
from ranking.skills import extract_normalized_skills
import numpy as np
import aiosqlite
import traceback

async def reprocess_queue():
    # Load FAISS index once
    index = FAISSIndex.load()

    # process jobs
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, title, embedding FROM jobs WHERE status!='queued'"
        )
        jobs = await cursor.fetchall()

        print(f"Processing {len(jobs)} jobs")

        for job_id, title, embedding in jobs:
            try:
                if not jobs:
                    continue

                if embedding is not None:

                    # Convert to buffer
                    embedding = np.frombuffer(embedding, dtype=np.float32)

                    # ADD TO FAISS
                    index.add(job_id, embedding)

                print("Processed:", title)

            except Exception as e:
                print("Failed:", title)
                print(f"Exception Type: {type(e).__name__}")
                print(f"Exception Message: {e}")
                print("Traceback:")
                print(traceback.format_exc())
    
    index.save()
    print("FAISS index updated")