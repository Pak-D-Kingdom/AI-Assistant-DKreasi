from app.services.fallback_service import FallbackService


def test_fallback_provides_whatsapp_url():
    fallback = FallbackService.get_fallback_response("l1")
    assert fallback["is_fallback"] is True
    assert "wa.me" in fallback["handoff_url"]
    assert "D-KREASI" in fallback["content"]
