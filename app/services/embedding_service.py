from typing import List
import numpy as np
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"SentenceTransformer not loaded ({e}). Using lightweight fallback.")
                self._model = "fallback"
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        model = self._get_model()
        if model != "fallback":
            embeddings = model.encode(texts, normalize_embeddings=True)
            return np.array(embeddings, dtype=np.float32)

        # Deterministic lightweight hash-based embedding fallback for offline / test
        dim = 384
        vectors = []
        for text in texts:
            np.random.seed(abs(hash(text)) % (2**32))
            v = np.random.randn(dim).astype(np.float32)
            v /= np.linalg.norm(v) + 1e-9
            vectors.append(v)
        return np.array(vectors, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        # Prepend 'query: ' for E5 instruction formatting
        formatted = f"query: {query}"
        return self.embed_texts([formatted])[0]
