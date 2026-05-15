import numpy as np

from ranking.skills import extract_normalized_skills
from ranking.cache import encode_and_cache
from job_ingestion.dedupe import JobDeduplicator

deduper = JobDeduplicator()


async def process_job(
    db,
    index,
    job_id,
    old_hash,
    data
):
    # Check bot detection

    if deduper.is_duplicate(data):
        print(f"Duplicate skipped: {data['title']}")
        return

    job_text = f"""
    {data['title']}
    {data['company']}
    {data['location']}
    {data['description']}
    """

    embedding, new_hash = encode_and_cache(
        job_text,
        old_hash
    )

    emb_blob = None

    if embedding is not None:

        embedding = embedding.astype("float32")

        norm = np.linalg.norm(embedding)

        if norm > 0:
            embedding = embedding / norm

        emb_blob = embedding.tobytes()
        
        print("FAISS score for url:", index.search(embedding, k=1)[0][0])
        index.add(job_id, embedding)

    skills_list = extract_normalized_skills(
        data["description"]
    )

    skills_str = ",".join(
        sorted(set(skills_list))
    )

    await db.execute("""
        UPDATE jobs
        SET
            title=?,
            company=?,
            location=?,
            description=?,
            skills=?,
            seniority=?,
            embedding=?,
            embedding_text_hash=?,
            status='done',
            show=1
        WHERE id=?
    """, (
        data["title"],
        data["company"],
        data["location"],
        data["description"],
        skills_str,
        data["seniority"],
        emb_blob,
        new_hash,
        job_id
    ))

    await db.commit()