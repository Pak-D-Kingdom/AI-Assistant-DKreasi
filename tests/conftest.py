import os
import pytest

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from app.services.embedding_service import EmbeddingService


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Ensure fast offline deterministic embeddings during all test runs."""
    EmbeddingService._shared_model = "fallback"
