from ranking.faiss_index import FAISSIndex

index = FAISSIndex().load()


def test_faiss_index():
    assert index.index.ntotal == len(index.job_ids)

def test_embedding():
    embedding = embed_text(data["embedding_text"])

    assert len(embedding) > 0

    assert embedding[:5]