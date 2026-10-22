import pytest
from app.services.rag_service import RagService


def test_l4_requires_tenant_id():
    rag = RagService()
    with pytest.raises(ValueError, match="Tenant ID is strictly required"):
        rag._get_namespace_dir(layer="l4", tenant_id=None)


def test_namespaces_are_strictly_isolated():
    rag = RagService()
    l1_path = rag._get_namespace_dir(layer="l1")
    l3_path = rag._get_namespace_dir(layer="l3")
    tenant_a_path = rag._get_namespace_dir(layer="l4", tenant_id="tenant_fnb_01")
    tenant_b_path = rag._get_namespace_dir(layer="l4", tenant_id="tenant_beauty_01")

    assert l1_path != l3_path
    assert tenant_a_path != tenant_b_path
    assert "l1_dkreasi" in l1_path
    assert "tenant_fnb_01" in tenant_a_path
    assert "tenant_beauty_01" in tenant_b_path
