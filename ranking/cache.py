import hashlib
from ranking.embeddings import get_embedding

def hash_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def should_update(old_hash, new_hash):
    return old_hash != new_hash


def encode_and_cache(text: str, old_hash: str = None):
    new_hash = hash_text(text)

    if old_hash == new_hash:
        return None, new_hash  # no recompute needed

    embedding = get_embedding(text)
    return embedding, new_hash