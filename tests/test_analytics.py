import pytest
from app.services.analytics_service import AnalyticsService


def test_calculate_kpis_zero_conversations():
    kpis = AnalyticsService.calculate_kpis(
        total_conversations=0,
        total_messages=0,
        total_tokens=0,
        avg_latency_ms=0.0,
        total_fallbacks=0,
        total_handoffs=0,
    )
    assert kpis["total_conversations"] == 0
    assert kpis["resolution_rate_percent"] == 100.0
    assert kpis["handoff_rate_percent"] == 0.0
    assert kpis["fallback_rate_percent"] == 0.0


def test_calculate_kpis_non_zero():
    kpis = AnalyticsService.calculate_kpis(
        total_conversations=100,
        total_messages=450,
        total_tokens=25000,
        avg_latency_ms=135.42,
        total_fallbacks=12,
        total_handoffs=8,
    )
    assert kpis["total_conversations"] == 100
    assert kpis["total_messages"] == 450
    assert kpis["total_tokens"] == 25000
    assert kpis["avg_latency_ms"] == 135.4
    assert kpis["fallback_rate_percent"] == 12.0
    assert kpis["resolution_rate_percent"] == 88.0
    assert kpis["handoff_rate_percent"] == 8.0


def test_render_dashboard_html():
    sample_data = {
        "period_days": 30,
        "kpis": {
            "total_conversations": 150,
            "total_messages": 820,
            "total_tokens": 64000,
            "avg_latency_ms": 115.2,
            "resolution_rate_percent": 92.5,
            "handoff_rate_percent": 7.5,
            "fallback_rate_percent": 7.5,
        },
        "layer_breakdown": {
            "l1": {"messages": 320, "tokens": 15000},
            "l2": {"messages": 210, "tokens": 12000},
            "l3": {"messages": 240, "tokens": 25000},
            "l4": {"messages": 50, "tokens": 12000},
        },
        "tenant_quotas": [
            {
                "tenant_id": "tenant_automotive_01",
                "name": "Bengkel PakDe Motor Jaya",
                "package_tier": "pixel",
                "monthly_quota": 500,
                "used_messages": 485,
                "remaining_messages": 15,
                "percentage_used": 97.0,
                "is_quota_exhausted": False,
            },
            {
                "tenant_id": "tenant_beauty_01",
                "name": "Glow Aesthetic Clinic",
                "package_tier": "pixel",
                "monthly_quota": 500,
                "used_messages": 505,
                "remaining_messages": 0,
                "percentage_used": 101.0,
                "is_quota_exhausted": True,
            },
        ],
        "top_questions": [
            {"query": "Harga pembuatan website katalog", "count": 28},
            {"query": "Berapa lama pengerjaan?", "count": 19},
        ],
        "unanswered_queries": [
            {"query": "Apakah bisa integrasi POS kasir offline?", "count": 5},
        ],
        "recent_activity": [],
        "hourly_traffic": [
            {
                "hour": "10:00",
                "hour_num": 10,
                "count": 45,
                "tenants": [
                    {"tenant_id": "tenant_automotive_01", "name": "Bengkel PakDe Motor Jaya", "count": 30},
                    {"tenant_id": "tenant_beauty_01", "name": "Glow Aesthetic Clinic", "count": 15},
                ],
            }
        ],
    }

    html = AnalyticsService.render_dashboard_html(sample_data, days=30)
    assert "<!DOCTYPE html>" in html
    assert "AI Engine Intelligence Dashboard" in html
    assert "92.5%" in html
    assert "7.5%" in html
    assert "Harga pembuatan website katalog" in html
    assert "Apakah bisa integrasi POS kasir offline?" in html
    assert "L1 · D-Kreasi Concierge" in html
    assert "L3 · Webia Sales AI" in html
    assert "Monitoring Kuota Klien (Tenant Quota Enforcement)" in html
    assert "Bengkel PakDe Motor Jaya" in html
    assert "Glow Aesthetic Clinic" in html
    assert "Habis (Blocked)" in html
    assert "Peak Hours Traffic" in html
    assert "Rincian Top Tenant (Maks 5)" in html
    assert "Waspada (≥80%)" in html
    assert "loadTrafficChart" in html
    assert "hourlyChartWrapper" in html
    assert "traffic-btn" in html
    assert "tenantDetailModal" in html
    assert "openTenantModal" in html
    assert "closeTenantModal" in html
    assert 'onclick="openTenantModal(this)"' in html
    assert "data-tenant=" in html
    assert "modalViewEdit" in html
    assert "globalAiModal" in html
    assert "switchModalTab" in html
    assert "saveTenantAiChanges" in html
    assert "saveGlobalAiSettings" in html
    assert "editTenantGreeting" in html
    assert "editTenantQuota" in html


def test_get_tenant_detail_info():
    detail = AnalyticsService._get_tenant_detail_info("tenant_automotive_01")
    assert "whatsapp" in detail
    assert "address" in detail
    assert "operating_hours" in detail
    assert "greeting" in detail
    assert detail["has_profil"] is True



def test_render_hourly_chart_svg():
    hourly_sample = [
        {
            "hour": "14:00",
            "hour_num": 14,
            "count": 55,
            "tenants": [
                {"tenant_id": "tenant_beauty_01", "name": "Glow Clinic", "count": 35},
                {"tenant_id": "tenant_auto_01", "name": "PakDe Motor", "count": 20},
            ],
        }
    ]
    svg = AnalyticsService._render_hourly_chart(hourly_sample)
    assert "<svg" in svg
    assert "Glow Clinic" in svg
    assert "PakDe Motor" in svg
    assert "55 chat" in svg
    assert "trafficAreaGradient" in svg
    assert "animate-chart-line" in svg
    assert "animate-chart-area" in svg


def test_render_traffic_chart_7_days():
    sample_7_days = {
        "period_days": 7,
        "max_count": 80,
        "traffic_points": [
            {"label": "Rab, 29/10", "tooltip_title": "📅 Rabu, 29 Okt 2026", "count": 40, "tenants": []},
            {"label": "Kam, 30/10", "tooltip_title": "📅 Kamis, 30 Okt 2026", "count": 80, "tenants": [{"name": "PakDe Motor", "count": 50}]},
            {"label": "Hari Ini", "tooltip_title": "📅 Jumat, 31 Okt 2026", "count": 25, "tenants": []},
        ],
        "x_ticks": [
            {"label": "Rab, 29/10"},
            {"label": "Kam, 30/10"},
            {"label": "Hari Ini"},
        ]
    }
    html = AnalyticsService._render_hourly_chart(sample_7_days, days=7)
    assert "<svg" in html
    assert "animate-chart-line" in html
    assert "Rab, 29/10" in html
    assert "Hari Ini" in html
    assert "Kamis, 30 Okt 2026" in html


def test_engine_config_endpoints():
    from app.api.v1.analytics import get_engine_config, save_engine_config, EngineConfigPayload
    cfg = get_engine_config()
    assert cfg["status"] == "success"
    assert "llm_model" in cfg
    assert "l1_prompt" in cfg
    assert "l4_prompt" in cfg

    # Test saving custom config
    payload = EngineConfigPayload(
        llm_temperature=0.35,
        ai_cs_whatsapp="628111222333"
    )
    saved = save_engine_config(payload)
    assert saved["status"] == "success"
    assert saved["config"]["llm_temperature"] == 0.35


def test_tenant_full_update_payload_schema():
    from app.api.v1.tenants import TenantAiFullUpdatePayload
    p = TenantAiFullUpdatePayload(
        name="Bengkel PakDe Motor Jaya",
        package_tier="vector",
        monthly_quota=1000,
        greeting="Halo! Selamat datang di bengkel kami.",
        reset_usage=True
    )
    assert p.package_tier == "vector"
    assert p.monthly_quota == 1000
    assert p.reset_usage is True

