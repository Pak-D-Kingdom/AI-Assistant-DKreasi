import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
from app.core.config import get_settings
from app.core.logging import logger
from app.services.embedding_service import EmbeddingService

settings = get_settings()


class RagService:
    _index_cache: Dict[str, Any] = {}
    _metadata_cache: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.base_path = settings.FAISS_BASE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    def _get_namespace_dir(self, layer: str, tenant_id: Optional[str] = None) -> str:
        # Strict namespace boundary enforcement (Default Deny)
        if layer == "l4":
            if not tenant_id:
                raise ValueError("Tenant ID is strictly required for layer L4.")
            path = os.path.join(self.base_path, "tenants", tenant_id)
        elif layer in ["l1", "l1_dkreasi"]:
            path = os.path.join(self.base_path, "l1_dkreasi")
        elif layer in ["l2", "l2_dkarsa"]:
            path = os.path.join(self.base_path, "l2_dkarsa")
        elif layer in ["l3", "l3_webia"]:
            path = os.path.join(self.base_path, "l3_webia")
        else:
            path = os.path.join(self.base_path, layer)

        os.makedirs(path, exist_ok=True)
        return path

    def preload(self, layer: str, tenant_id: Optional[str] = None):
        """Preload metadata and FAISS index into memory cache during startup."""
        ns_dir = self._get_namespace_dir(layer, tenant_id)
        meta_file = os.path.join(ns_dir, "metadata.json")
        faiss_file = os.path.join(ns_dir, "index.faiss")

        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    self._metadata_cache[ns_dir] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to preload metadata for {ns_dir}: {e}")

        if os.path.exists(faiss_file):
            try:
                import faiss
                self._index_cache[ns_dir] = faiss.read_index(faiss_file)
                logger.info(f"Preloaded FAISS index for {layer} into memory.")
            except Exception as e:
                logger.warning(f"Failed to preload FAISS index for {ns_dir}: {e}")

    def save_index(
        self,
        layer: str,
        chunks: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ):
        ns_dir = self._get_namespace_dir(layer, tenant_id)
        texts = [f"passage: {c['content']}" for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        try:
            import faiss
            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)  # Inner Product (Cosine similarity when normalized)
            index.add(embeddings)
            faiss_path = os.path.join(ns_dir, "index.faiss")
            faiss.write_index(index, faiss_path)
            self._index_cache[ns_dir] = index
        except ImportError:
            # Fallback if faiss-cpu is building
            np.save(os.path.join(ns_dir, "index.npy"), embeddings)

        meta_path = os.path.join(ns_dir, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        self._metadata_cache[ns_dir] = chunks

        logger.info(f"Saved FAISS index for {layer} (tenant={tenant_id}) with {len(chunks)} chunks.")

    def search(
        self,
        query: str,
        layer: str,
        tenant_id: Optional[str] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        ns_dir = self._get_namespace_dir(layer, tenant_id)

        # Retrieve metadata (from cache or disk)
        if ns_dir in self._metadata_cache:
            chunks = self._metadata_cache[ns_dir]
        else:
            meta_file = os.path.join(ns_dir, "metadata.json")
            if not os.path.exists(meta_file):
                return []
            with open(meta_file, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            self._metadata_cache[ns_dir] = chunks

        if not chunks:
            return []

        query_vec = self.embedding_service.embed_query(query).reshape(1, -1)

        # Retrieve FAISS index (from cache or disk)
        faiss_file = os.path.join(ns_dir, "index.faiss")
        if ns_dir in self._index_cache or os.path.exists(faiss_file):
            try:
                import faiss
                if ns_dir not in self._index_cache:
                    self._index_cache[ns_dir] = faiss.read_index(faiss_file)
                index = self._index_cache[ns_dir]

                scores, indices = index.search(query_vec, min(top_k, len(chunks)))
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(chunks):
                        chunk = dict(chunks[idx])
                        chunk["score"] = float(score)
                        results.append(chunk)
                return results
            except Exception as e:
                logger.warning(f"FAISS search failed: {e}. Falling back to NumPy.")

        # NumPy fallback
        npy_file = os.path.join(ns_dir, "index.npy")
        if os.path.exists(npy_file):
            embeddings = np.load(npy_file)
            scores = np.dot(embeddings, query_vec.T).flatten()
            top_indices = np.argsort(scores)[::-1][:top_k]
            results = []
            for idx in top_indices:
                chunk = dict(chunks[idx])
                chunk["score"] = float(scores[idx])
                results.append(chunk)
            return results

        # Simple text match fallback
        return chunks[:top_k]

    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        if not retrieved_chunks:
            return ""

        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            title = chunk.get("title", f"Document {i}")
            content = chunk.get("content", "").strip()
            context_blocks.append(f"[Konteks Pengetahuan: {title}]\n{content}")

        return "\n\n".join(context_blocks)
