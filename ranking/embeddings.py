import numpy as np
from sentence_transformers import SentenceTransformer

# Load once (IMPORTANT for performance)
_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> np.ndarray:
    """
    Returns a normalized embedding vector for text.
    """
    if not text:
        return np.zeros(384)

    return np.array(_model.encode(text, normalize_embeddings=True))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Cosine similarity between two embeddings.
    """
    if a is None or b is None:
        return 0.0

    return float(np.dot(a, b))