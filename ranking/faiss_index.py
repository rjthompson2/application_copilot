import os
import faiss
import json
import numpy as np
import aiosqlite
from config import DB_NAME, FAISS_INDEX_PATH, FAISS_META_PATH

async def build_faiss_index():
    index = FAISSIndex(dim=384)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, embedding FROM jobs WHERE embedding IS NOT NULL"
        )
        rows = await cursor.fetchall()

    valid = 0
    skipped = 0

    for job_id, emb_blob in rows:
        if not emb_blob:
            skipped += 1
            continue

        embedding = np.frombuffer(emb_blob, dtype=np.float32)

        # critical safety check
        if embedding.shape[0] != 384:
            print(f"Bad embedding for job {job_id}: {embedding.shape}")
            skipped += 1
            continue

        index.add(job_id, embedding)
        valid += 1

    print(f"FAISS index built: {valid} vectors, {skipped} skipped")

    return index

async def get_or_build_index():
    if os.path.exists(FAISS_INDEX_PATH):
        print("Loading FAISS index...")
        return FAISSIndex.load()

    print("Building FAISS index...")
    index = FAISSIndex()

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id, embedding FROM jobs WHERE embedding IS NOT NULL"
        )
        rows = await cursor.fetchall()

    for job_id, emb_blob in rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        index.add(job_id, emb)

    index.save()
    return index

class FAISSIndex:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.job_ids = []

    def add(self, job_id: int, embedding: np.ndarray):
        if embedding.shape[0] != self.dim:
            print(f"Skipping job {job_id}: wrong dim {embedding.shape}")
            return

        vec = embedding.astype("float32").reshape(1, -1)
        self.index.add(vec)
        self.job_ids.append(job_id)

    def search(self, embedding: np.ndarray, k=10):
        if len(self.job_ids) == 0:
            return []

        vec = embedding.astype("float32").reshape(1, -1)

        scores, indices = self.index.search(vec, k)

        results = []
        for score, i in zip(scores[0], indices[0]):
            if i == -1 or i >= len(self.job_ids):
                continue

            results.append({
                "job_id": self.job_ids[i],
                "faiss_score": float(score)
            })

        return results
    
    def save(self):
        if self.index is None:
            print("No index to save")
            return

        faiss.write_index(self.index, str(FAISS_INDEX_PATH))

        with open(FAISS_META_PATH, "w") as f:
            json.dump(self.job_ids, f)

    @classmethod
    def load(cls):
        if not os.path.exists(FAISS_INDEX_PATH):
            return cls()

        index = cls()
        index.index = faiss.read_index(FAISS_INDEX_PATH)

        with open(FAISS_META_PATH, "r") as f:
            index.job_ids = json.load(f)

        return index