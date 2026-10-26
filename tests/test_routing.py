import pytest
from app.layers.l1_dkreasi.tools import L1IntentRouter


def test_detects_website_intent():
    decision = L1IntentRouter.detect_and_route("Saya butuh website untuk mengembangkan usaha kafe saya")
    assert decision["intent"] == L1IntentRouter.INTENT_WEBSITE
    assert decision["action"] == "navigate"
    assert "/webia" in decision["target_url"]
    assert "category=fnb" in decision["target_url"]
    assert "Website Bisnis" in decision["button_text"]


def test_detects_invitation_intent():
    decision = L1IntentRouter.detect_and_route("Bisa bantu buat undangan pernikahan online dengan fitur RSVP?")
    assert decision["intent"] == L1IntentRouter.INTENT_INVITATION
    assert decision["action"] == "navigate"
    assert "/undangan" in decision["target_url"]
    assert "event=pernikahan" in decision["target_url"]
    assert "Undangan Digital" in decision["button_text"]


def test_detects_coming_soon_intent():
    decision = L1IntentRouter.detect_and_route("Apakah ada jasa buat aplikasi mobile android atau video editing?")
    assert decision["intent"] == L1IntentRouter.INTENT_COMING_SOON
    assert decision["action"] == "inform"
    assert decision["target_url"] is None


def test_detects_customer_support_intent():
    decision = L1IntentRouter.detect_and_route("Saya mau kontak customer service lewat whatsapp")
    assert decision["intent"] == L1IntentRouter.INTENT_SUPPORT
    assert decision["action"] == "handoff"
    assert "wa.me" in decision["target_url"]


def test_detects_ambiguous_greeting():
    decision = L1IntentRouter.detect_and_route("Halo selamat siang, saya butuh informasi")
    assert decision["intent"] == L1IntentRouter.INTENT_CLARIFICATION
    assert decision["action"] == "clarify"
    assert "Undangan Digital" in decision["clarification_question"]
    assert "Website Bisnis" in decision["clarification_question"]
