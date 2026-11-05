import pytest
from unittest.mock import AsyncMock, patch

from app.core.context import RequestContext
from app.pipeline.orchestrator import PipelineOrchestrator
from app.services.embedding_service import EmbeddingService
from app.services.semantic_cache_service import SemanticCacheService, get_semantic_cache


@pytest.fixture
def cache_service():
    EmbeddingService._shared_model = "fallback"
    cache = SemanticCacheService()
    cache.invalidate()  # Clean state
    return cache


@pytest.mark.asyncio
async def test_exact_normalized_match(cache_service):
    # Simpan FAQ jam buka
    await cache_service.set(
        layer="l4",
        query="Buka jam berapa bengkel ini?",
        response="Bengkel PakDe Motor buka setiap Senin - Sabtu pukul 08:00 - 17:00 WIB.",
        tenant_id="tenant_automotive_01",
    )

    # Query dengan variasi kapitalisasi dan tanpa tanda tanya
    hit = await cache_service.get(
        layer="l4",
        query="buka jam berapa bengkel ini",
        tenant_id="tenant_automotive_01",
    )

    assert hit is not None
    assert hit["match_type"] == "exact"
    assert hit["similarity"] == 1.0
    assert "08:00 - 17:00" in hit["response"]
    assert hit["latency_ms"] < 50


@pytest.mark.asyncio
async def test_semantic_similarity_match(cache_service):
    # Simulasikan embedding vector dengan kemiripan cosinus ~0.95
    import numpy as np
    base_vec = np.zeros(384, dtype=np.float32)
    base_vec[0] = 1.0

    similar_vec = np.zeros(384, dtype=np.float32)
    similar_vec[0] = 0.95
    similar_vec[1] = float(np.sqrt(1 - 0.95**2))

    def mock_embed(q: str):
        if "Berapa biaya" in q:
            return base_vec
        return similar_vec

    cache_service.embedding_service.embed_query = mock_embed

    # Simpan FAQ harga
    await cache_service.set(
        layer="l4",
        query="Berapa biaya servis motor matic?",
        response="Biaya servis tune-up motor matic mulai dari Rp45.000 (belum termasuk oli).",
        tenant_id="tenant_automotive_01",
    )

    # Query dengan kalimat yang sedikit berbeda tapi intinya sama
    hit = await cache_service.get(
        layer="l4",
        query="Biaya servis motor matic berapa ya?",
        tenant_id="tenant_automotive_01",
        threshold=0.75,
    )

    assert hit is not None
    assert "Rp45.000" in hit["response"]
    assert hit["match_type"] == "semantic"
    assert hit["similarity"] >= 0.75


@pytest.mark.asyncio
async def test_tenant_isolation_in_cache(cache_service):
    # Simpan FAQ di tenant beauty
    await cache_service.set(
        layer="l4",
        query="Lokasi kliniknya di mana?",
        response="Glow Aesthetic Clinic berlokasi di Jl. Dharmawangsa No. 12, Surabaya.",
        tenant_id="tenant_beauty_01",
    )

    # Tenant automotive menanyakan pertanyaan yang sama
    hit_automotive = await cache_service.get(
        layer="l4",
        query="Lokasi kliniknya di mana?",
        tenant_id="tenant_automotive_01",
    )

    # Harus MISS karena beda tenant namespace (Isolasi data 100%)
    assert hit_automotive is None

    # Sedangkan tenant beauty harus HIT
    hit_beauty = await cache_service.get(
        layer="l4",
        query="Lokasi kliniknya di mana?",
        tenant_id="tenant_beauty_01",
    )
    assert hit_beauty is not None
    assert "Jl. Dharmawangsa" in hit_beauty["response"]


@pytest.mark.asyncio
async def test_cache_invalidation(cache_service):
    await cache_service.set(
        layer="l4",
        query="Apa syarat reservasi meja?",
        response="Reservasi meja minimal 2 jam sebelumnya via WhatsApp.",
        tenant_id="tenant_fnb_01",
    )

    # Sebelum invalidasi -> HIT
    hit_before = await cache_service.get(
        layer="l4",
        query="Apa syarat reservasi meja?",
        tenant_id="tenant_fnb_01",
    )
    assert hit_before is not None

    # Invalidasi tenant fnb
    cache_service.invalidate(tenant_id="tenant_fnb_01")

    # Setelah invalidasi -> MISS
    hit_after = await cache_service.get(
        layer="l4",
        query="Apa syarat reservasi meja?",
        tenant_id="tenant_fnb_01",
    )
    assert hit_after is None


@pytest.mark.asyncio
async def test_orchestrator_cache_hit_avoids_llm_call(cache_service):
    mock_llm = AsyncMock()
    mock_llm.chat.return_value = {
        "content": "Kami beralamat di Jalan Merdeka No. 45 Jakarta Pusat.",
        "usage": {"prompt_tokens": 120, "completion_tokens": 25, "total_tokens": 145},
        "latency_ms": 1200,
        "provider": "openai",
        "model": "gpt-4o-mini",
        "is_fallback": False,
    }

    orchestrator = PipelineOrchestrator(
        llm_service=mock_llm,
        cache_service=cache_service,
    )

    context = RequestContext(
        site_id="site_auto_1",
        site_name="PakDe Motor",
        layer="l4",
        tenant_id="tenant_automotive_01",
    )

    # Panggilan Pertama -> Cache MISS -> LLM dipanggil
    res1 = await orchestrator.execute(
        messages=[{"role": "user", "content": "Di mana alamat bengkel?"}],
        context=context,
    )
    assert res1["success"] is True
    assert mock_llm.chat.call_count == 1
    assert "Jalan Merdeka" in res1["message"]["content"]

    # Panggilan Kedua dengan pertanyaan yang persis/normal -> Cache HIT -> LLM TIDAK dipanggil!
    res2 = await orchestrator.execute(
        messages=[{"role": "user", "content": "di mana alamat bengkel"}],
        context=context,
    )
    assert res2["success"] is True
    # LLM call_count harus tetap 1 (hemat token, tidak ada panggilan baru)
    assert mock_llm.chat.call_count == 1
    assert res2["meta"].get("is_cached") is True
    assert res2["meta"].get("provider") == "semantic-cache"
    assert "Jalan Merdeka" in res2["message"]["content"]
