import json
import os
import re
import threading
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

from app.core.config import get_settings
from app.core.logging import logger
from app.services.embedding_service import EmbeddingService

settings = get_settings()

TENANT_ID_RE = re.compile(r"^tenant_[a-z0-9_]{1,60}$")
LAYER_NAME_RE = re.compile(r"^[a-z0-9_]{1,40}$")


class RagService:
    _index_cache: Dict[str, Any] = {}
    _metadata_cache: Dict[str, List[Dict[str, Any]]] = {}
    _mtime_cache: Dict[str, Tuple[float, float, float]] = {}
    _lock = threading.RLock()

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.base_path = settings.FAISS_BASE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    # ------------------------------------------------------------------
    # Namespace & cache
    # ------------------------------------------------------------------
    def _get_namespace_dir(self, layer: str, tenant_id: Optional[str] = None, create: bool = True) -> str:
        # Strict namespace boundary enforcement (Default Deny)
        layer = str(getattr(layer, "value", layer) or "").strip().lower()

        if layer == "l4":
            if not tenant_id:
                raise ValueError("Tenant ID is strictly required for layer L4.")
            if not TENANT_ID_RE.match(tenant_id):
                raise ValueError("Invalid tenant ID format.")
            path = os.path.join(self.base_path, "tenants", tenant_id)
        elif layer in ["l1", "l1_dkreasi"]:
            path = os.path.join(self.base_path, "l1_dkreasi")
        elif layer in ["l2", "l2_dkarsa"]:
            path = os.path.join(self.base_path, "l2_dkarsa")
        elif layer in ["l3", "l3_webia"]:
            path = os.path.join(self.base_path, "l3_webia")
        else:
            if not LAYER_NAME_RE.match(layer):
                raise ValueError("Invalid layer name.")
            path = os.path.join(self.base_path, layer)

        # Pastikan path tidak keluar dari folder dasar (anti path traversal)
        base_abs = os.path.abspath(self.base_path)
        if not os.path.abspath(path).startswith(base_abs + os.sep):
            raise ValueError("Namespace path is outside of the index base path.")

        if create:
            os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def _mtimes(ns_dir: str) -> Tuple[float, float, float]:
        def mt(name: str) -> float:
            p = os.path.join(ns_dir, name)
            return os.path.getmtime(p) if os.path.exists(p) else 0.0

        return (mt("metadata.json"), mt("index.faiss"), mt("index.npy"))

    def _refresh_cache_if_stale(self, ns_dir: str) -> None:
        """Buang cache bila file index/metadata berubah (mis. di-rebuild lewat script terpisah)."""
        current = self._mtimes(ns_dir)
        if self._mtime_cache.get(ns_dir) != current:
            self._metadata_cache.pop(ns_dir, None)
            self._index_cache.pop(ns_dir, None)
            self._mtime_cache[ns_dir] = current

    def _load_metadata(self, ns_dir: str) -> List[Dict[str, Any]]:
        if ns_dir in self._metadata_cache:
            return self._metadata_cache[ns_dir]
        meta_file = os.path.join(ns_dir, "metadata.json")
        if not os.path.exists(meta_file):
            return []
        with open(meta_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        self._metadata_cache[ns_dir] = chunks
        return chunks

    @staticmethod
    def _atomic_write_json(path: str, data: Any) -> None:
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    # ------------------------------------------------------------------
    # Preload & save
    # ------------------------------------------------------------------
    def preload(self, layer: str, tenant_id: Optional[str] = None):
        """Preload metadata and FAISS index into memory cache during startup."""
        ns_dir = self._get_namespace_dir(layer, tenant_id)
        with self._lock:
            self._refresh_cache_if_stale(ns_dir)

            try:
                self._load_metadata(ns_dir)
            except Exception as e:
                logger.warning(f"Failed to preload metadata for {ns_dir}: {e}")

            faiss_file = os.path.join(ns_dir, "index.faiss")
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
        faiss_path = os.path.join(ns_dir, "index.faiss")
        npy_path = os.path.join(ns_dir, "index.npy")
        meta_path = os.path.join(ns_dir, "metadata.json")

        # Buang chunk yang hanya berisi judul (mis. "# Nama Bisnis - FAQ"). Chunk seperti ini
        # tidak berisi informasi, tetapi skor kemiripannya tinggi untuk query berisi nama bisnis
        # sehingga memakan slot top_k.
        def _is_heading_only(content: Any) -> bool:
            lines = [ln.strip() for ln in str(content or "").splitlines() if ln.strip()]
            return bool(lines) and all(ln.startswith("#") for ln in lines)

        chunks = [c for c in chunks if not _is_heading_only(c.get("content", ""))]

        with self._lock:
            # Hapus index lama agar tidak tersisa index usang yang tidak cocok dengan metadata baru
            for old in (faiss_path, npy_path):
                if os.path.exists(old):
                    os.remove(old)
            self._index_cache.pop(ns_dir, None)
            self._metadata_cache.pop(ns_dir, None)

            if not chunks:
                self._atomic_write_json(meta_path, [])
                self._mtime_cache[ns_dir] = self._mtimes(ns_dir)
                logger.info(f"Cleared index for {layer} (tenant={tenant_id}); no chunks.")
                return

            texts = [f"passage: {c['content']}" for c in chunks]
            embeddings = np.ascontiguousarray(self.embedding_service.embed_texts(texts), dtype="float32")

            try:
                import faiss
                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim)  # Inner Product (Cosine similarity when normalized)
                index.add(embeddings)
                tmp_faiss = f"{faiss_path}.tmp"
                faiss.write_index(index, tmp_faiss)
                os.replace(tmp_faiss, faiss_path)
                self._index_cache[ns_dir] = index
            except ImportError:
                # Fallback if faiss-cpu is not available
                tmp_npy = f"{npy_path}.tmp.npy"
                np.save(tmp_npy, embeddings)
                os.replace(tmp_npy, npy_path)

            self._atomic_write_json(meta_path, chunks)
            self._metadata_cache[ns_dir] = chunks
            self._mtime_cache[ns_dir] = self._mtimes(ns_dir)

        logger.info(f"Saved FAISS index for {layer} (tenant={tenant_id}) with {len(chunks)} chunks.")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        layer: str,
        tenant_id: Optional[str] = None,
        top_k: int = 3,
        min_score: Optional[float] = None,
        return_all_if_leq: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        return_all_if_leq: bila jumlah chunk namespace <= nilai ini, kembalikan SEMUA chunk
        (cocok untuk knowledge tenant yang kecil, sehingga pertanyaan singkat tidak gagal retrieval).
        """
        ns_dir = self._get_namespace_dir(layer, tenant_id, create=False)  # jangan buat folder saat membaca
        if not os.path.isdir(ns_dir):
            return []

        with self._lock:
            self._refresh_cache_if_stale(ns_dir)
            chunks = self._load_metadata(ns_dir)

        if not chunks:
            return []

        if return_all_if_leq and len(chunks) <= return_all_if_leq:
            return [dict(c, score=1.0) for c in chunks]

        top_k = max(1, min(top_k, len(chunks)))
        query_vec = np.ascontiguousarray(
            self.embedding_service.embed_query(query).reshape(1, -1), dtype="float32"
        )

        # --- FAISS ---
        faiss_file = os.path.join(ns_dir, "index.faiss")
        if ns_dir in self._index_cache or os.path.exists(faiss_file):
            try:
                import faiss
                with self._lock:
                    if ns_dir not in self._index_cache:
                        self._index_cache[ns_dir] = faiss.read_index(faiss_file)
                    index = self._index_cache[ns_dir]

                if index.ntotal != len(chunks):
                    logger.warning(
                        f"Index/metadata mismatch for {ns_dir}: {index.ntotal} vectors vs {len(chunks)} chunks. "
                        "Jalankan re-index."
                    )

                scores, indices = index.search(query_vec, top_k)
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if 0 <= idx < len(chunks):
                        if min_score is not None and float(score) < min_score:
                            continue
                        chunk = dict(chunks[idx])
                        chunk["score"] = float(score)
                        results.append(chunk)
                return results
            except Exception as e:
                logger.warning(f"FAISS search failed: {e}. Falling back to NumPy.")

        # --- NumPy fallback ---
        npy_file = os.path.join(ns_dir, "index.npy")
        if os.path.exists(npy_file):
            embeddings = np.load(npy_file)
            if embeddings.shape[0] == len(chunks):
                scores = np.dot(embeddings, query_vec.T).flatten()
                top_indices = np.argsort(scores)[::-1][:top_k]
                results = []
                for idx in top_indices:
                    if min_score is not None and float(scores[idx]) < min_score:
                        continue
                    chunk = dict(chunks[idx])
                    chunk["score"] = float(scores[idx])
                    results.append(chunk)
                return results
            logger.warning(f"NumPy index/metadata mismatch for {ns_dir}. Jalankan re-index.")

        # --- Keyword overlap fallback (tanpa index vektor) ---
        words = {w for w in re.findall(r"\w+", query.lower()) if len(w) > 2}
        scored = []
        for c in chunks:
            text = f"{c.get('title', '')} {c.get('content', '')}".lower()
            hits = sum(1 for w in words if w in text)
            if hits:
                scored.append((hits, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(c, score=float(h)) for h, c in scored[:top_k]]

    # ------------------------------------------------------------------
    # Profil tenant (nama & WhatsApp) dari knowledge yang tersimpan
    # ------------------------------------------------------------------
    def get_profile(self, layer: str, tenant_id: Optional[str] = None) -> Dict[str, str]:
        try:
            ns_dir = self._get_namespace_dir(layer, tenant_id, create=False)
            if not os.path.isdir(ns_dir):
                return {}
            with self._lock:
                self._refresh_cache_if_stale(ns_dir)
                chunks = self._load_metadata(ns_dir)
        except Exception as e:
            logger.warning(f"get_profile failed: {e}")
            return {}

        text = "\n".join(str(c.get("content", "")) for c in chunks)

        def grab(pattern: str) -> str:
            m = re.search(pattern, text)
            val = m.group(1).strip() if m else ""
            return "" if val in ("", "-") else val

        profile = {
            "name": grab(r"\*\*Nama Bisnis\*\*:\s*(.+)"),
            "whatsapp": grab(r"\*\*WhatsApp[^*]*\*\*:\s*(.+)"),
        }
        return {k: v for k, v in profile.items() if v}

    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        if not retrieved_chunks:
            return ""

        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            title = chunk.get("title", f"Document {i}")
            content = chunk.get("content", "").strip()
            context_blocks.append(f"[Konteks Pengetahuan: {title}]\n{content}")

        return "\n\n".join(context_blocks)