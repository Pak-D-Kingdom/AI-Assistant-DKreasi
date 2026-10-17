import pytest
from app.layers.l3_webia.brief_service import BusinessBriefService, BusinessBriefSchema
from app.layers.l3_webia.tools import L3IntentRouter, generate_business_brief


def test_brief_creation_success():
    data = {
        "business_name": "Kopi Seduh Nusantara",
        "category": "F&B",
        "description": "Coffee shop kekinian dengan biji kopi lokal pilihan dan suasana tenang.",
        "target_audience": "Mahasiswa, pekerja remote, dan penikmat kopi",
        "package_recommendation": "Paket Pulse (Rp899.000)",
        "features_needed": ["Menu interaktif", "WhatsApp Order", "Google Maps", "Galeri Suasana"],
        "location": "Bandung, Jawa Barat",
        "operating_hours": "Setiap Hari, 08:00 - 22:00 WIB",
        "contact_whatsapp": "08123456789",
        "social_media": "@kopiseduh.id",
    }

    result = BusinessBriefService.create_brief(data)

    assert result["status"] == "success"
    assert result["brief_id"].startswith("BRIEF-")
    assert "Kopi Seduh Nusantara" in result["markdown_display"]
    assert "Pulse (Rp899.000)" in result["markdown_display"]
    assert "https://wa.me/" in result["whatsapp_url"]
    assert "Kopi+Seduh+Nusantara" in result["whatsapp_url"] or "Kopi%20Seduh%20Nusantara" in result["whatsapp_url"]
    
    # Verifikasi L4 Tenant Seed
    l4_seed = result["l4_tenant_seed"]
    assert l4_seed["tenant_name"] == "Kopi Seduh Nusantara"
    assert l4_seed["category"] == "f&b"
    assert len(l4_seed["features_requested"]) == 4


def test_brief_intent_routing():
    queries = [
        "bisa bantu buatkan brief website?",
        "saya ingin susun business brief",
        "buat brief untuk cafe saya",
        "isi formulir kebutuhan website",
    ]

    for q in queries:
        route = L3IntentRouter.detect_and_route(q)
        assert route["intent"] == "business_brief_request"
        assert route["action"] == "brief"
        assert "Business Brief" in route["service_name"]


def test_generate_business_brief_tool():
    payload = {
        "business_name": "Klinik Sehat Bersama",
        "category": "Healthcare",
        "description": "Layanan dokter umum dan gigi dengan pendaftaran online.",
        "package_recommendation": "Paket Nexus (Rp1.499.000)",
        "features_needed": ["Jadwal Dokter", "Booking Pasien", "Dashboard CMS"],
    }

    brief = generate_business_brief(payload)
    assert brief["status"] == "success"
    assert brief["data"]["business_name"] == "Klinik Sehat Bersama"
    assert brief["data"]["category"] == "Healthcare"
    assert "Nexus" in brief["data"]["package_recommendation"]
