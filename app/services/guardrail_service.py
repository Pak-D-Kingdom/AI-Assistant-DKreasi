import re
from typing import Dict, Any


class GuardrailService:
    def __init__(self):
        # 1. Prompt Injection & Jailbreak (Hard Security Violation)
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
            "dan mode aktif",
        ]

        # 2. Out-of-Scope Abuse (Menjadikan chatbot bisnis sebagai ChatGPT tugas umum)
        self.abuse_patterns = [
            "buatkan kode",
            "buatkan script",
            "tuliskan kode",
            "write code",
            "bikin coding",
            "buatkan program python",
            "buatkan program java",
            "buatkan program c++",
            "kerjakan tugas sekolah",
            "kerjakan pr ",
            "buatkan esai",
            "tuliskan esai",
            "buatkan cerpen",
            "buatkan puisi",
        ]

    def inspect_input(self, user_input: str) -> Dict[str, Any]:
        normalized = user_input.lower()
        for pattern in self.injection_patterns:
            if pattern in normalized:
                return {
                    "safe": False,
                    "category": "injection",
                    "reason": "Permintaan terdeteksi melanggar batasan keamanan sistem (prompt injection attempt).",
                    "sanitized": user_input,
                }

        for pattern in self.abuse_patterns:
            if pattern in normalized:
                return {
                    "safe": False,
                    "category": "out_of_scope",
                    "reason": "Permintaan terdeteksi di luar lingkup layanan asisten bisnis (out-of-scope task abuse).",
                    "sanitized": user_input,
                }

        return {
            "safe": True,
            "category": "safe",
            "reason": None,
            "sanitized": user_input.strip(),
        }

    def inspect_output(self, layer: str, output: str) -> str:
        # L1: Enforce anti-promise launch dates for Coming Soon services
        if layer in ["l1", "l1_dkreasi"]:
            output = re.sub(
                r"(akan|pasti|dijadwalkan)\s+(rilis|meluncur|hadir|tersedia)\s+(pada\s+tanggal|bulan\s+depan|tahun\s+depan|\d{1,2}\s+[a-zA-Z]+\s+\d{4})",
                "sedang dalam tahap persiapan dan pengembangan oleh tim D-KREASI",
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

        # White-Labeling Guardrail: Cegah kebocoran nama vendor backend LLM pihak ketiga
        platform_name = "D'Karsa" if layer in ["l2", "l2_dkarsa"] else ("D-Kreasi" if layer in ["l1", "l1_dkreasi"] else "WEBIA")
        output = re.sub(
            r"(?:via\s+API\s+resmi\s*)?\(\s*(?:Google\s+Gemini|OpenAI|ChatGPT|Claude|Anthropic)(?:\s*/\s*(?:Google\s+Gemini|OpenAI|ChatGPT|Claude|Anthropic))*\s*\)",
            f"yang dikembangkan dan dikelola khusus oleh tim {platform_name}",
            output,
            flags=re.IGNORECASE,
        )
        output = re.sub(
            r"\b(?:Google\s+Gemini|OpenAI|ChatGPT|GPT-4o?|Claude|Anthropic)\b",
            "teknologi AI cerdas",
            output,
            flags=re.IGNORECASE,
        )

        # Anti-PakDe Group Guardrail: Cegah penyebutan "PakDe Group" di seluruh layer (D'Karsa, Webia, D-Kreasi)
        output = re.sub(
            r"\b(?:dari\s+|by\s+|milik\s+|ekosistem\s+)?PakDe\s+Group\b",
            platform_name,
            output,
            flags=re.IGNORECASE,
        )
        output = re.sub(
            r"\bPakDe\s+Group\b",
            platform_name,
            output,
            flags=re.IGNORECASE,
        )

        return output
