from typing import Dict, Any, Optional
from app.services.handoff_service import HandoffService


class L4IntentRouter:
    """Intent detection and action router for Layer 4 AI Business Chatbot."""
    INTENT_BOOKING = "booking_inquiry"
    INTENT_PRICE = "pricing_inquiry"
    INTENT_LOCATION = "location_hours"
    INTENT_WHATSAPP = "whatsapp_handoff"
    INTENT_GENERAL = "general_inquiry"

    @classmethod
    def detect_and_route(cls, query: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        normalized = query.lower().strip()

        # WhatsApp Handoff
        if any(w in normalized for w in ["whatsapp", "wa", "kontak", "hubungi", "admin", "cs", "telepon", "nomor"]):
            return {
                "intent": cls.INTENT_WHATSAPP,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url("Halo, saya ingin bertanya lebih lanjut mengenai layanan bisnis Anda."),
                "button_text": "Hubungi CS WhatsApp Bisnis →",
            }

        # Booking / Reservasi
        if any(w in normalized for w in ["booking", "reservasi", "pesan tempat", "janji temu", "jadwal", "antrean"]):
            return {
                "intent": cls.INTENT_BOOKING,
                "action": "booking",
                "target_url": HandoffService.get_whatsapp_url("Halo, saya ingin melakukan booking / reservasi layanan."),
                "button_text": "Ajukan Reservasi / Booking →",
            }

        # Default general
        return {
            "intent": cls.INTENT_GENERAL,
            "action": "inform",
            "target_url": None,
            "button_text": None,
        }
