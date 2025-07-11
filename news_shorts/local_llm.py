from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from . import config


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    model_name = config.LOCAL_EMBED_MODEL
    config.logger.info(f"Loading local embed model: {model_name}")
    return SentenceTransformer(model_name)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return vector embeddings for given texts using a local model."""
    model = _load_model()
    emb = model.encode(texts, show_progress_bar=False)
    return emb.tolist()
