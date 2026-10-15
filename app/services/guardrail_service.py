import re
from typing import Dict, Any


class GuardrailService:
    def __init__(self):
        self.injection_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "bypass instructions",
            "show system prompt",
            "print system prompt",
            "tampilkan system prompt",
            "bocorkan prompt",
            "abaikan instruksi sebelumnya",
            "forget rules",
            "jailbreak",
            "developer mode on",
            "override instructions",
        ]

    def inspect_input(self, user_input: str) -> Dict[str, Any]:
        normalized = user_input.lower()
        for pattern in self.injection_patterns:
            if pattern in normalized:
                return {
                    "safe": False,
                    "reason": "Permintaan terdeteksi melanggar batasan keamanan sistem (prompt injection attempt).",
                    "sanitized": user_input,
                }
        return {
            "safe": True,
            "reason": None,
            "sanitized": user_input.strip(),
        }

    def inspect_output(self, layer: str, output: str) -> str:
        # L1: Enforce anti-promise launch dates for Coming Soon services
        if layer in ["l1", "l1_dkreasi"]:
            output = re.sub(
                r"(akan|pasti|dijadwalkan)\s+(rilis|meluncur|hadir|tersedia)\s+(pada\s+tanggal|bulan\s+depan|tahun\s+depan|\d{1,2}\s+[a-zA-Z]+\s+\d{4})",
                "sedang dalam tahap persiapan dan pengembangan oleh tim PakDe Group",
                output,
                flags=re.IGNORECASE,
            )

        # L3: Enforce anti-false SEO promise for WEBIA
        if layer in ["l3", "l3_webia"]:
            output = re.sub(
                r"(dijamin|pasti|menjamin)\s+(masuk|dapat|ada di)?\s*ranking\s*(#?1|satu|pertama)\s*(di)?\s*google",
                "membantu meningkatkan visibilitas website di mesin pencari Google",
                output,
                flags=re.IGNORECASE,
            )

        return output
