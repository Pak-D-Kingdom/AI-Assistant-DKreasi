from typing import Dict, Any, List
from app.services.handoff_service import HandoffService


class L1IntentRouter:
    INTENT_WEBSITE = "need_website"
    INTENT_INVITATION = "need_invitation"
    INTENT_CLARIFICATION = "need_clarification"
    INTENT_COMING_SOON = "coming_soon"
    INTENT_SUPPORT = "customer_support"

    INTENT_KEYWORDS: Dict[str, List[str]] = {
        INTENT_INVITATION: [
            "undangan", "nikah", "pernikahan", "wedding", "akad", "resepsi",
            "khitan", "khitanan", "sunat", "ulang tahun", "ultah", "birthday",
            "anniversary", "aqiqah", "wisuda", "graduation", "selebrasi",
            "acara keluarga", "undangan online", "rsvp", "tamu undangan",
        ],
        INTENT_WEBSITE: [
            "website", "web", "landing page", "toko online", "bengkel", "restoran",
            "resto", "cafe", "kafe", "salon", "klinik", "properti", "kontraktor",
            "company profile", "profil bisnis", "bisnis", "umkm", "usaha", "jualan",
            "katalog produk", "seo", "ecommerce", "webia", "perusahaan", "agency",
        ],
        INTENT_COMING_SOON: [
            "coming soon", "layanan lain", "layanan baru", "kapan rilis", "aplikasi mobile",
            "aplikasi android", "aplikasi ios", "desain logo", "video editing",
        ],
        INTENT_SUPPORT: [
            "whatsapp", "wa", "customer service", "cs", "hubungi admin", "kontak admin",
            "chat admin", "bicara manusia", "kontak cs", "telepon", "keluhan", "komplain",
        ],
    }

    @classmethod
    def detect_and_route(cls, query: str) -> Dict[str, Any]:
        normalized = query.lower().strip()

        scores = {intent: 0 for intent in cls.INTENT_KEYWORDS}
        for intent, keywords in cls.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in normalized:
                    scores[intent] += 1

        top_intent = max(scores, key=scores.get)
        if scores[top_intent] > 0:
            return cls._build_payload(top_intent, 0.95, query=normalized)

        return {
            "intent": cls.INTENT_CLARIFICATION,
            "confidence": 0.5,
            "action": "clarify",
            "target_url": None,
            "button_text": None,
            "service_name": None,
            "clarification_question": "Apakah Anda sedang membutuhkan Undangan Digital untuk acara spesial atau Website Bisnis untuk mengembangkan usaha Anda?",
        }

    @classmethod
    def _build_payload(cls, intent: str, confidence: float, query: str = "") -> Dict[str, Any]:
        normalized = query.lower()
        if intent == cls.INTENT_WEBSITE:
            # Context pre-filler detection (industry / category hint)
            cat_param = "general"
            if any(w in normalized for w in ["kafe", "cafe", "kopi", "resto", "makanan", "kuliner"]):
                cat_param = "fnb"
            elif any(w in normalized for w in ["salon", "barber", "klinik", "beauty", "skincare"]):
                cat_param = "beauty"
            elif any(w in normalized for w in ["bengkel", "otomotif", "motor", "mobil"]):
                cat_param = "automotive"
            elif any(w in normalized for w in ["toko", "retail", "baju", "olshop", "produk"]):
                cat_param = "retail"
            elif any(w in normalized for w in ["petshop", "kucing", "anjing", "hewan"]):
                cat_param = "pet-animal-service"

            target_url = f"/webia?source=ai_concierge&intent=need_website&category={cat_param}"
            return {
                "intent": cls.INTENT_WEBSITE,
                "confidence": confidence,
                "action": "navigate",
                "target_url": target_url,
                "button_text": "Jelajahi Website Bisnis (WEBIA) →",
                "service_name": "Website Bisnis (WEBIA)",
                "context_params": {
                    "source": "ai_concierge",
                    "intent": "need_website",
                    "category": cat_param,
                },
                "clarification_question": None,
            }
        elif intent == cls.INTENT_INVITATION:
            event_param = "pernikahan"
            if any(w in normalized for w in ["ulang tahun", "ultah", "sweet 17", "milad"]):
                event_param = "ulang_tahun"
            elif any(w in normalized for w in ["khitan", "sunat"]):
                event_param = "khitanan"
            elif any(w in normalized for w in ["aqiqah"]):
                event_param = "aqiqah"
            elif any(w in normalized for w in ["wisuda"]):
                event_param = "wisuda"
            elif any(w in normalized for w in ["haji", "umroh", "safar"]):
                event_param = "walimatus_safar"

            target_url = f"/undangan?source=ai_concierge&intent=need_invitation&event={event_param}"
            return {
                "intent": cls.INTENT_INVITATION,
                "confidence": confidence,
                "action": "navigate",
                "target_url": target_url,
                "button_text": "Konsultasi Undangan Digital (D'Karsa) →",
                "service_name": "Undangan Digital (D'Karsa)",
                "context_params": {
                    "source": "ai_concierge",
                    "intent": "need_invitation",
                    "event": event_param,
                },
                "clarification_question": None,
            }
        elif intent == cls.INTENT_COMING_SOON:
            return {
                "intent": cls.INTENT_COMING_SOON,
                "confidence": confidence,
                "action": "inform",
                "target_url": None,
                "button_text": None,
                "service_name": "Layanan Lainnya (Coming Soon)",
                "clarification_question": None,
            }
        elif intent == cls.INTENT_SUPPORT:
            return {
                "intent": cls.INTENT_SUPPORT,
                "confidence": confidence,
                "action": "handoff",
                "target_url": HandoffService.get_whatsapp_url(),
                "button_text": "Hubungi Customer Support WhatsApp →",
                "service_name": "Customer Support PakDe Group",
                "clarification_question": None,
            }
        else:
            return {
                "intent": cls.INTENT_CLARIFICATION,
                "confidence": 0.5,
                "action": "clarify",
                "target_url": None,
                "button_text": None,
                "service_name": None,
                "clarification_question": "Apakah Anda membutuhkan Undangan Digital atau Website Bisnis?",
            }
