import pytest
from app.services.usage_service import UsageService


def test_l1_l2_l3_unlimited_quota():
    for layer in ["l1", "l2", "l3"]:
        res = UsageService.evaluate_quota(layer=layer, tenant_id=None, current_usage=99999)
        assert res["allowed"] is True
        assert res["remaining"] is None


def test_tenant_under_pixel_quota():
    res = UsageService.evaluate_quota(
        layer="l4",
        tenant_id="tenant_beauty_01",
        current_usage=42,
        package_tier="pixel",
    )
    assert res["allowed"] is True
    assert res["usage"] == 42
    assert res["quota"] == 500
    assert res["remaining"] == 458
    assert res["package_tier"] == "pixel"


def test_tenant_exceeds_pixel_quota():
    res = UsageService.evaluate_quota(
        layer="l4",
        tenant_id="tenant_automotive_01",
        current_usage=500,
        package_tier="pixel",
    )
    assert res["allowed"] is False
    assert res["usage"] == 500
    assert res["quota"] == 500
    assert res["remaining"] == 0
    assert "telah mencapai batas maksimal" in res["message"]


def test_tenant_custom_tiers():
    # Pulse: 1500 limit
    res_pulse = UsageService.evaluate_quota(
        layer="l4",
        tenant_id="tenant_fnb_01",
        current_usage=1499,
        package_tier="pulse",
    )
    assert res_pulse["allowed"] is True
    assert res_pulse["remaining"] == 1
    assert res_pulse["quota"] == 1500

    # Nexus: 2500 limit
    res_nexus = UsageService.evaluate_quota(
        layer="l4",
        tenant_id="tenant_company_01",
        current_usage=2500,
        package_tier="nexus",
    )
    assert res_nexus["allowed"] is False
    assert res_nexus["quota"] == 2500

    # Infinity: 5000 limit
    res_infinity = UsageService.evaluate_quota(
        layer="l4",
        tenant_id="tenant_tech_01",
        current_usage=4999,
        package_tier="infinity",
    )
    assert res_infinity["allowed"] is True
    assert res_infinity["remaining"] == 1
    assert res_infinity["quota"] == 5000


def test_quota_cache_and_invalidation():
    tenant_id = "test_cache_tenant_99"
    UsageService.clear_quota_cache()
    
    # Set cache directly
    cache_key = f"{tenant_id}_2026_11"
    UsageService._QUOTA_CACHE[cache_key] = {
        "cached_at": 9999999999.0,
        "result": {"allowed": True, "remaining": 123, "quota": 500, "usage": 377},
    }
    
    assert cache_key in UsageService._QUOTA_CACHE
    UsageService.invalidate_quota_cache(tenant_id)
    assert cache_key not in UsageService._QUOTA_CACHE
