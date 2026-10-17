import urllib.parse
from app.layers.l3_webia.tools import recommend_webia_solution, L3IntentRouter, WEBIA_PACKAGES
from app.layers.l3_webia.brief_service import BusinessBriefService, BusinessBriefSchema


def test_fnb_recommendation_matrix():
    # Base entry recommendation for F&B
    rec = recommend_webia_solution("fnb")
    assert rec["category"] == "F&B (Food & Beverages)"
    assert rec["recommended_package"] == "Paket Pulse"
    assert "F01" in rec["recommended_template"]
    assert "Booking Meja / Reservasi" in rec["recommended_modules"]

    # F&B with CMS request -> Nexus
    rec_cms = recommend_webia_solution("fnb", needs_cms=True)
    assert rec_cms["recommended_package"] == "Paket Nexus"
    assert "CMS" in rec_cms["type"]


def test_company_recommendation_matrix():
    # Company profile entry is Nexus (PRD §7.6)
    rec = recommend_webia_solution("company")
    assert "Company" in rec["category"]
    assert rec["recommended_package"] == "Paket Nexus"
    assert "C01" in rec["recommended_template"]


def test_custom_scale_triggers_infinity():
    rec = recommend_webia_solution("retail", needs_custom=True)
    assert rec["recommended_package"] == "Paket Infinity"
    assert rec["price"] == "Rp2.499.000"


def test_l3_routes_to_fnb_solution():
    res = L3IntentRouter.detect_and_route("Saya butuh website untuk cafe kopi kekinian")
    assert res["intent"] == "recommend_fnb_website"
    assert res["action"] == "navigate"
    assert "#koleksi-template" in res["target_url"]
    assert res["recommendation"]["recommended_package"] == "Paket Pulse"


def test_l3_routes_to_automotive_solution():
    res = L3IntentRouter.detect_and_route("Saya punya bengkel mobil dan butuh landing page")
    assert res["intent"] == "recommend_automotive_website"
    assert res["action"] == "navigate"
    assert "A01" in res["recommendation"]["recommended_template"]


def test_l3_brief_creation():
    data = {
        "business_name": "Kopi Senja Utama",
        "category": "F&B",
        "description": "Artisan coffee shop dan tempat santai mahasiswa",
        "features_needed": ["Menu Display", "Reservasi Meja", "Tombol WhatsApp"],
        "contact_whatsapp": "081234567890",
        "location": "Surabaya",
    }
    brief = BusinessBriefService.create_brief(data)
    assert brief["status"] == "success"
    assert "BRIEF-" in brief["brief_id"]
    unquoted_wa = urllib.parse.unquote(brief["whatsapp_url"])
    assert "Kopi Senja Utama" in unquoted_wa
    assert brief["l4_tenant_seed"]["category"] == "f&b"
