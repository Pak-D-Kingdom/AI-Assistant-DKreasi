import pytest
from app.services.rag_service import RagService
from app.layers.l3_webia.prompts import get_l3_system_prompt
from app.core.context import RequestContext


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


def test_l3_context_aware_hosting_prompt_injection():
    context = RequestContext(
        layer="l3_webia",
        hosting_status={
            "domain": "tokokita.webia.id",
            "status": "aktif",
            "expires_at": "2027-12-31",
            "is_paid": True,
        }
    )
    prompt = get_l3_system_prompt(context=context)
    assert "CONTEXT-AWARE HOSTING STATUS" in prompt
    assert "tokokita.webia.id" in prompt
    assert "sudah lunas" in prompt
