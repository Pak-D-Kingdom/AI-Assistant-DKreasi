import re
import urllib.parse
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class HandoffService:
    @staticmethod
    def get_whatsapp_url(custom_message: Optional[str] = None) -> str:
        raw_number = settings.AI_CS_WHATSAPP
        wa_number = re.sub(r"\D+", "", raw_number)
        message = custom_message or settings.AI_CS_DEFAULT_MESSAGE
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{wa_number}?text={encoded_message}"
