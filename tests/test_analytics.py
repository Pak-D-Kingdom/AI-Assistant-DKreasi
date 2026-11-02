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
    assert "Waspada (≥80%)" in html
