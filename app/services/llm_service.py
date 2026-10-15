import time
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


class LlmService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.base_url = settings.LLM_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        start_time = time.time()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        # Mock Provider
        if self.provider == "mock":
            return {
                "content": "Halo! Saya AI Assistant resmi D-KREASI. Ada yang bisa saya bantu terkait Undangan Digital atau Website Bisnis?",
                "provider": "mock",
                "model": "mock-v1",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                "latency_ms": int((time.time() - start_time) * 1000),
                "is_fallback": False,
            }

        # Standard OpenAI-compatible HTTP REST (e.g. 9router / Ollama / OpenAI)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

                return {
                    "content": content,
                    "provider": "llm",
                    "model": data.get("model", self.model),
                    "usage": usage,
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "is_fallback": False,
                }
        except Exception as e:
            logger.error(f"LLM Provider error: {str(e)}. Triggering fallback.")
            return {
                "content": "Halo! Saya AI Assistant resmi D-KREASI by PakDe Group. Kami siap membantu Anda memilih layanan Website Bisnis atau Undangan Digital terbaik.",
                "provider": "fallback",
                "model": "fallback-safe",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": int((time.time() - start_time) * 1000),
                "is_fallback": True,
                "error_message": str(e),
            }
