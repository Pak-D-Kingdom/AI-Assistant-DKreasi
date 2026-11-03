from app.layers.l2_dkarsa.tools import L2IntentRouter


def test_l2_routes_to_catalog_on_wedding_intent():
    res = L2IntentRouter.detect_and_route("Saya mau buat undangan pernikahan")
    assert res["intent"] == "wedding_invitation"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#desain"


def test_l2_routes_to_whatsapp_on_javanese_royal():
    res = L2IntentRouter.detect_and_route("Ada tema jawa keraton 3D?")
    assert res["intent"] == "wedding_javanese_royal"
    assert res["action"] == "handoff"
    assert "https://wa.me/" in res["target_url"]
    assert "3D%20Javanese%20Royal" in res["target_url"]


def test_l2_routes_to_birthday_intent():
    res = L2IntentRouter.detect_and_route("Mau bikin undangan ulang tahun sweet 17")
    assert res["intent"] == "birthday_invitation"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#desain"


def test_l2_routes_to_khitanan_intent():
    res = L2IntentRouter.detect_and_route("Bisa buat undangan khitanan anak?")
    assert res["intent"] == "khitanan_invitation"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#desain"


def test_l2_routes_to_whatsapp_on_order_inquiry():
    res = L2IntentRouter.detect_and_route("Bagaimana cara order undangan?")
    assert res["intent"] == "order_consultation"
    assert res["action"] == "handoff"
    assert "https://wa.me/" in res["target_url"]


def test_l2_routes_to_specific_templates():
    res_jawa = L2IntentRouter.detect_and_route("Ada tema adat jawa geometris?")
    assert res_jawa["action"] in ["handoff", "navigate"]

    res_rustic = L2IntentRouter.detect_and_route("Mau tema rustic coral peach untuk sweet 17")
    assert res_rustic["intent"] == "birthday_invitation"
    assert res_rustic["target_url"] == "#desain"


def test_l2_routes_to_payment_inquiry():
    res = L2IntentRouter.detect_and_route("Bisa bayar pakai QRIS atau transfer BCA?")
    assert res["intent"] == "payment_inquiry"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#harga"
    assert "Midtrans" in res["service_name"]


def test_l2_routes_to_online_builder():
    res = L2IntentRouter.detect_and_route("Saya mau buat undangan sendiri online lewat form builder")
    assert res["intent"] == "online_builder"
    assert res["target_url"] == "/buat-undangan"


def test_l2_routes_to_rsvp_wish():
    res = L2IntentRouter.detect_and_route("Bagaimana cara tamu konfirmasi rsvp dan kirim doa restu?")
    assert res["intent"] == "rsvp_wish_feature"
    assert "wish_wall" in res["data"]


def test_l2_theme_has_demo_url():
    from app.layers.l2_dkarsa.tools import DKARSA_THEMES
    assert all("demo_url" in t for t in DKARSA_THEMES)


def test_l2_routes_to_gallery_feature_inquiry():
    res = L2IntentRouter.detect_and_route("Bagaimana cara upload foto galeri dan berapa maksimal fotonya?")
    assert res["intent"] == "gallery_feature_inquiry"
    assert res["target_url"] == "/buat-undangan"
    assert "multiple_upload" in res["data"]
    assert "reordering" in res["data"]
    assert "basic" in res["data"]["quota_by_package"]


def test_l2_routes_to_safar_umrah():
    res = L2IntentRouter.detect_and_route("Bisa buat undangan walimatussafar umrah keluarga?")
    assert res["intent"] == "keagamaan_invitation"
    assert res["target_url"] == "#desain"


def test_l2_builder_checklist_updated():
    from app.layers.l2_dkarsa.tools import get_builder_checklist
    chk = get_builder_checklist()
    step3 = next(s for s in chk["steps"] if s["step"] == 3)
    items_str = " ".join(step3["items"])
    assert "WEBP" in items_str
    assert "Reorder" in items_str
