import time
import re
import string
from typing import Optional, Dict, Any, List
import numpy as np

from app.core.logging import logger
from app.services.embedding_service import EmbeddingService


class SemanticCacheEntry:
    def __init__(
        self,
        query: str,
        response: str,
        embedding: np.ndarray,
        layer: str,
        tenant_id: Optional[str] = None,
        ttl_seconds: int = 86400 * 7,  # Default 7 hari
    ):
        self.query = query
        self.normalized_query = self.normalize_text(query)
        self.response = response
        self.embedding = embedding
        self.layer = layer
        self.tenant_id = tenant_id
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds
        self.hit_count = 0

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalisasi teks: huruf kecil, hapus tanda baca, dan satukan spasi."""
        text = text.lower().strip()
        text = re.sub(r"[%s]" % re.escape(string.punctuation), " ", text)
        return " ".join(text.split())

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class SemanticCacheService:
    """
    Semantic Caching Engine untuk mempercepat respon FAQ dan menghemat token LLM.
    - Level 1: Normalized Exact Match (O(1) Memory Lookup, <1ms).
    - Level 2: Cosine Similarity Vector Match (Embedding Dot-Product, <20ms).
    - Isolasi Penuh: Cache di-namespace per layer & per tenant.
    """

    SIMILARITY_THRESHOLD: float = 0.88  # Ambang batas kemiripan semantik (88%)
    MAX_ENTRIES_PER_NAMESPACE: int = 200

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        # In-memory storage: { namespace_key: List[SemanticCacheEntry] }
        self._cache: Dict[str, List[SemanticCacheEntry]] = {}
        # Metrics tracking
        self.stats = {
            "total_lookups": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_saved_estimate": 0,
            "total_latency_saved_ms": 0,
        }

    def _get_namespace(self, layer: str, tenant_id: Optional[str] = None) -> str:
        """Membuat namespace isolasi ketat antar-tenant dan antar-layer."""
        layer_norm = (layer or "l1").lower()
        if tenant_id:
            return f"{layer_norm}_{tenant_id}"
        return f"{layer_norm}_global"

    def get_stats(self) -> Dict[str, Any]:
        """Mengembalikan metrik performa semantic cache."""
        total = self.stats["total_lookups"]
        hits = self.stats["cache_hits"]
        hit_ratio = round((hits / total) * 100, 1) if total > 0 else 0.0
        return {
            "total_lookups": total,
            "cache_hits": hits,
            "cache_misses": self.stats["cache_misses"],
            "hit_ratio_percent": hit_ratio,
            "tokens_saved_estimate": self.stats["tokens_saved_estimate"],
            "total_latency_saved_ms": self.stats["total_latency_saved_ms"],
            "cached_namespaces": len(self._cache),
            "total_cached_entries": sum(len(entries) for entries in self._cache.values()),
        }

    async def get(
        self,
        layer: str,
        query: str,
        tenant_id: Optional[str] = None,
        threshold: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Mencari jawaban semantik di cache.
        Returns:
            Dict dengan response, similarity, latency_ms, atau None jika miss.
        """
        start_time = time.time()
        self.stats["total_lookups"] += 1

        query_clean = query.strip()
        if len(query_clean) < 3:
            self.stats["cache_misses"] += 1
            return None

        namespace = self._get_namespace(layer, tenant_id)
        entries = self._cache.get(namespace, [])
        if not entries:
            self.stats["cache_misses"] += 1
            return None

        # Bersihkan entri yang sudah expired
        active_entries = [e for e in entries if not e.is_expired()]
        if len(active_entries) != len(entries):
            self._cache[namespace] = active_entries
            entries = active_entries

        norm_query = SemanticCacheEntry.normalize_text(query_clean)

        # LEVEL 1: Exact Normalized Match (< 1ms)
        for entry in entries:
            if entry.normalized_query == norm_query:
                entry.hit_count += 1
                self.stats["cache_hits"] += 1
                self.stats["tokens_saved_estimate"] += 350
                latency = int((time.time() - start_time) * 1000)
                self.stats["total_latency_saved_ms"] += 1200
                logger.info(f"[SemanticCache] Exact HIT for '{query_clean}' (namespace={namespace}, latency={latency}ms)")
                return {
                    "response": entry.response,
                    "matched_query": entry.query,
                    "match_type": "exact",
                    "similarity": 1.0,
                    "latency_ms": max(1, latency),
                }

        # LEVEL 2: Vector Cosine Similarity Match (< 20ms)
        try:
            query_vector = self.embedding_service.embed_query(query_clean)
            if query_vector is None:
                self.stats["cache_misses"] += 1
                return None

            sim_threshold = threshold or self.SIMILARITY_THRESHOLD
            best_entry: Optional[SemanticCacheEntry] = None
            highest_sim = -1.0

            for entry in entries:
                # Cosine similarity pada unit vector: dot product
                sim = float(np.dot(query_vector, entry.embedding))
                if sim > highest_sim:
                    highest_sim = sim
                    best_entry = entry

            if best_entry and highest_sim >= sim_threshold:
                best_entry.hit_count += 1
                self.stats["cache_hits"] += 1
                self.stats["tokens_saved_estimate"] += 350
                latency = int((time.time() - start_time) * 1000)
                self.stats["total_latency_saved_ms"] += 1200
                logger.info(
                    f"[SemanticCache] Semantic HIT ({highest_sim:.3f} >= {sim_threshold}) "
                    f"query='{query_clean}' matched='{best_entry.query}' (latency={latency}ms)"
                )
                return {
                    "response": best_entry.response,
                    "matched_query": best_entry.query,
                    "match_type": "semantic",
                    "similarity": round(highest_sim, 3),
                    "latency_ms": max(1, latency),
                }

        except Exception as e:
            logger.warning(f"[SemanticCache] Error calculating similarity: {e}")

        self.stats["cache_misses"] += 1
        return None

    async def set(
        self,
        layer: str,
        query: str,
        response: str,
        tenant_id: Optional[str] = None,
        ttl_seconds: int = 86400 * 7,
    ) -> bool:
        """
        Menyimpan pasangan pertanyaan dan jawaban ke semantic cache.
        Akan mengabaikan respon fallback, penolakan kuota, atau jawaban error.
        """
        if not query or not response:
            return False

        # Jangan simpan respon penolakan / fallback / kuota habis
        forbidden_keywords = [
            "kuota layanan asisten chat otomatis bulan ini",
            "maaf, saya tidak menemukan informasi",
            "hubungi kami langsung via whatsapp",
            "terjadi kesalahan sistem",
        ]
        resp_lower = response.lower()
        if any(fk in resp_lower for fk in forbidden_keywords):
            return False

        # Jangan simpan query yang terlalu pendek
        if len(query.strip()) < 4:
            return False

        namespace = self._get_namespace(layer, tenant_id)
        if namespace not in self._cache:
            self._cache[namespace] = []

        entries = self._cache[namespace]

        # Cek jika normalized query sudah ada, update responsenya saja
        norm_query = SemanticCacheEntry.normalize_text(query)
        for existing in entries:
            if existing.normalized_query == norm_query:
                existing.response = response
                existing.created_at = time.time()
                existing.expires_at = existing.created_at + ttl_seconds
                return True

        # Hitung vector embedding untuk query baru
        try:
            query_vector = self.embedding_service.embed_query(query)
            if query_vector is None:
                return False

            new_entry = SemanticCacheEntry(
                query=query.strip(),
                response=response.strip(),
                embedding=query_vector,
                layer=layer,
                tenant_id=tenant_id,
                ttl_seconds=ttl_seconds,
            )

            # Evict LRU jika melebihi batas maksimal entri per namespace
            if len(entries) >= self.MAX_ENTRIES_PER_NAMESPACE:
                entries.sort(key=lambda x: (x.hit_count, x.created_at))
                entries.pop(0)

            entries.append(new_entry)
            logger.debug(f"[SemanticCache] Stored new entry for query='{query}' (namespace={namespace})")
            return True
        except Exception as e:
            logger.warning(f"[SemanticCache] Failed to store cache entry: {e}")
            return False

    def invalidate(self, layer: Optional[str] = None, tenant_id: Optional[str] = None):
        """Menghapus cache untuk namespace tertentu (misal saat knowledge tenant di-update)."""
        if layer and tenant_id:
            ns = self._get_namespace(layer, tenant_id)
            self._cache.pop(ns, None)
            logger.info(f"[SemanticCache] Invalidated cache for namespace '{ns}'")
        elif tenant_id:
            to_remove = [k for k in self._cache if k.endswith(f"_{tenant_id}")]
            for k in to_remove:
                self._cache.pop(k, None)
            logger.info(f"[SemanticCache] Invalidated all cache namespaces for tenant '{tenant_id}'")
        elif layer:
            to_remove = [k for k in self._cache if k.startswith(f"{layer.lower()}_")]
            for k in to_remove:
                self._cache.pop(k, None)
            logger.info(f"[SemanticCache] Invalidated all cache namespaces for layer '{layer}'")
        else:
            self._cache.clear()
            logger.info("[SemanticCache] Cleared all semantic caches globally")


_shared_cache_instance: Optional[SemanticCacheService] = None


def get_semantic_cache() -> SemanticCacheService:
    """Mengembalikan singleton instance SemanticCacheService untuk seluruh aplikasi."""
    global _shared_cache_instance
    if _shared_cache_instance is None:
        _shared_cache_instance = SemanticCacheService()
    return _shared_cache_instance

