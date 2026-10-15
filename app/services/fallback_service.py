from typing import Optional
from app.services.handoff_service import HandoffService


class FallbackService:
    @staticmethod
    def get_fallback_response(layer: str) -> dict:
        handoff_url = HandoffService.get_whatsapp_url()

        if layer in ["l1", "l1_dkreasi"]:
            content = (
                "Halo! Saya AI Assistant resmi D-KREASI by PakDe Group. "
                "Saat ini sistem sedang melakukan penyesuaian jaringan. "
                "Anda dapat menjelajahi layanan Website Bisnis dan Undangan Digital kami, "
                "atau menghubungi Customer Support kami langsung via WhatsApp."
            )
        elif layer in ["l2", "l2_dkarsa"]:
            content = (
                "Halo! Saya Asisten Undangan Digital D-Karsa. "
                "Jika membutuhkan bantuan mendesak seputar pemesanan undangan, "
                "tim CS kami siap membantu Anda melalui WhatsApp."
            )
        elif layer in ["l3", "l3_webia"]:
            content = (
                "Halo! Saya Sales AI WEBIA. "
                "Kami siap membantu kebutuhan website profesional Anda. "
                "Silakan tinggalkan pesan atau konsultasikan langsung dengan tim sales kami di WhatsApp."
            )
        else:
            content = (
                "Mohon maaf, asisten bisnis kami sedang dalam pemeliharaan. "
                "Silakan hubungi kontak resmi kami untuk informasi lebih lanjut."
            )

        return {
            "content": content,
            "provider": "fallback",
            "model": "fallback-safe",
            "is_fallback": True,
            "handoff_url": handoff_url,
        }
