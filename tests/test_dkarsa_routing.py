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


def test_l2_routes_to_catalog_on_birthday_intent():
    res = L2IntentRouter.detect_and_route("Mau bikin undangan ulang tahun sweet 17")
    assert res["intent"] == "birthday_invitation"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#desain"


def test_l2_routes_to_catalog_on_khitanan_intent():
    res = L2IntentRouter.detect_and_route("Bisa buat undangan khitanan anak?")
    assert res["intent"] == "khitanan_invitation"
    assert res["action"] == "navigate"
    assert res["target_url"] == "#desain"


def test_l2_routes_to_whatsapp_on_order_inquiry():
    res = L2IntentRouter.detect_and_route("Bagaimana cara order undangan?")
    assert res["intent"] == "order_consultation"
    assert res["action"] == "handoff"
    assert "https://wa.me/" in res["target_url"]
