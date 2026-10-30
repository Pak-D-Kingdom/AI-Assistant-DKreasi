import urllib.parse
from app.layers.l3_webia.tools import recommend_webia_solution, L3IntentRouter, WEBIA_PACKAGES
from app.layers.l3_webia.brief_service import BusinessBriefService, BusinessBriefSchema


def test_fnb_recommendation_matrix():
    # Base entry recommendation for F&B
    rec = recommend_webia_solution("fnb")
    assert rec["category"] == "F&B (Food & Beverages)"
    assert rec["recommended_package"] == "Paket Pulse"
    assert "Little Corner" in rec["recommended_template"] or "F01" in rec["recommended_template"]
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
    assert "Northstar" in rec["recommended_template"]


def test_custom_scale_triggers_infinity():
    rec = recommend_webia_solution("retail", needs_custom=True)
    assert rec["recommended_package"] == "Paket Infinity"
    assert rec["price"] == "Rp2.499.000"


def test_pixel_package_pricing():
    from app.layers.l3_webia.tools import WEBIA_PACKAGES
    pixel = next(p for p in WEBIA_PACKAGES if p["id"] == "pixel")
    assert pixel["price"] == 499000
    assert pixel["price_formatted"] == "Rp499.000"


def test_l3_routes_to_fnb_solution():
    res = L3IntentRouter.detect_and_route("Saya butuh website untuk cafe kopi kekinian")
    assert res["intent"] == "recommend_fnb_website"
    assert res["action"] == "navigate"
    assert "#koleksi-template" in res["target_url"]
    assert res["recommendation"]["recommended_package"] == "Paket Pulse"
    assert "cart_template_slug" in res


def test_l2_guest_calculator():
    from app.layers.l2_dkarsa.tools import calculate_guest_tier
    res_large = calculate_guest_tier(350)
    assert res_large["tier"] == "eksklusif"
    assert "Paket Eksklusif" in res_large["recommended_package"]

    res_small = calculate_guest_tier(50)
    assert res_small["tier"] == "premium"
    assert "Paket Premium" in res_small["recommended_package"]


def test_l2_builder_checklist():
    from app.layers.l2_dkarsa.tools import get_builder_checklist
    checklist = get_builder_checklist()
    assert "Checklist" in checklist["title"]
    assert len(checklist["steps"]) == 4


def test_l2_intent_routes_to_guest_calculator():
    from app.layers.l2_dkarsa.tools import L2IntentRouter
    res = L2IntentRouter.detect_and_route("Tamu undangan saya sekitar 350 orang")
    assert res["intent"] == "guest_calculator"
    assert res["calculation"]["tier"] == "eksklusif"

    res_pricing = L2IntentRouter.detect_and_route("Berapa harga paket undangan?")
    assert res_pricing["intent"] == "guest_calculator"
    assert "calculation" in res_pricing


def test_l2_intent_routes_to_checklist():
    from app.layers.l2_dkarsa.tools import L2IntentRouter
    res = L2IntentRouter.detect_and_route("Data apa saja yang perlu disiapkan untuk buat undangan?")
    assert res["intent"] == "builder_checklist"
    assert "steps" in res["data"]


def test_l3_routes_to_automotive_solution():
    res = L3IntentRouter.detect_and_route("Saya punya bengkel mobil dan butuh landing page")
    assert res["intent"] == "recommend_automotive_website"
    assert res["action"] == "navigate"
    assert "Pitstop" in res["recommendation"]["recommended_template"]


def test_l3_routes_to_petshop_solution():
    res = L3IntentRouter.detect_and_route("Saya mau buat website petshop toko makanan kucing")
    assert res["intent"] == "recommend_petshop_website"
    assert res["action"] == "navigate"
    assert "PawMart" in res["recommendation"]["recommended_template"]


def test_l3_routes_to_dental_solution():
    res = L3IntentRouter.detect_and_route("Bisa bikin website untuk klinik dokter gigi?")
    assert res["intent"] == "recommend_dental_website"
    assert res["action"] == "navigate"
    assert "Dental" in res["recommendation"]["recommended_template"]


def test_l3_routes_to_technology_solution():
    res = L3IntentRouter.detect_and_route("Saya punya perusahaan software house dan butuh website profil IT")
    assert res["intent"] == "recommend_technology_website"
    assert res["action"] == "navigate"
    assert "AzuraCraft" in res["recommendation"]["recommended_template"] or "Software House" in res["recommendation"]["recommended_template"]
    assert res["recommendation"]["recommended_package"] == "Paket Nexus"


def test_l3_routes_to_customer_account_and_orders():
    res_orders = L3IntentRouter.detect_and_route("Di mana saya bisa cek status pesanan website saya?")
    assert res_orders["intent"] == "customer_order_tracking"
    assert res_orders["action"] == "navigate"
    assert res_orders["target_url"] == "/dashboard"

    res_auth = L3IntentRouter.detect_and_route("Bagaimana cara login akun saya?")
    assert res_auth["intent"] == "customer_auth"
    assert res_auth["action"] == "navigate"
    assert res_auth["target_url"] == "/login"


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


def test_l3_routes_to_laundry_home_services():
    res = L3IntentRouter.detect_and_route("Saya mau buat website untuk usaha laundry kiloan dan cuci sepatu antar jemput")
    assert res["intent"] == "recommend_home_services_website"
    assert res["action"] == "navigate"
    assert "Laundry" in res["recommendation"]["category"]
    assert "Mint Fresh" in res["recommendation"]["recommended_template"] or "Baby Blue" in res["recommendation"]["recommended_template"]
    assert res["cart_template_slug"] == "laundry-mint-fresh"


def test_l3_routes_to_agriculture_farming():
    res = L3IntentRouter.detect_and_route("Saya butuh website untuk peternakan sapi potong dan kambing qurban modern")
    assert res["intent"] == "recommend_agriculture_website"
    assert res["action"] == "navigate"
    assert "Agriculture" in res["recommendation"]["category"]
    assert "Agriternak" in res["recommendation"]["recommended_template"]
    assert res["cart_template_slug"] == "agriternak-bold-livestock"


def test_l3_routes_to_payment_checkout_inquiry():
    res = L3IntentRouter.detect_and_route("Bisa bayar pakai QRIS atau transfer via Midtrans?")
    assert res["intent"] == "payment_checkout_inquiry"
    assert res["action"] == "navigate"
    assert res["target_url"] == "/orders/create"
    assert "Midtrans" in res["service_name"]


def test_l3_routes_to_addon_inquiry():
    res = L3IntentRouter.detect_and_route("Apa saja pilihan add-on fitur tambahan resmi di Webia?")
    assert res["intent"] == "addon_inquiry"
    assert len(res["data"]["addons"]) == 4
    assert any(a["id"] == "seo-optimization" for a in res["data"]["addons"])


def test_l3_customer_auth_guest_checkout():
    res = L3IntentRouter.detect_and_route("Bagaimana cara daftar akun?")
    assert res["intent"] == "customer_auth"
    assert "/orders/create" in res["data"]["guest_checkout_url"]
