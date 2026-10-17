import time
import asyncio
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
        layer: Optional[str] = None,
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

                # Robust parsing: handles both 9router SSE event-stream and standard JSON
                import json
                raw_text = response.text.strip()
                content = ""
                model_used = self.model
                usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

                # Handle Server-Sent Events (SSE) stream (e.g. 9router combos return text/event-stream)
                if raw_text.startswith("data:") or "text/event-stream" in response.headers.get("content-type", ""):
                    content_parts = []
                    for line in raw_text.splitlines():
                        line = line.strip()
                        if line.startswith("data:") and not line.startswith("data: [DONE]"):
                            chunk_str = line[5:].strip()
                            if chunk_str:
                                try:
                                    chunk_json = json.loads(chunk_str)
                                    if "model" in chunk_json:
                                        model_used = chunk_json["model"]
                                    if "usage" in chunk_json and chunk_json["usage"]:
                                        usage = chunk_json["usage"]
                                    delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                                    if "content" in delta and delta["content"]:
                                        content_parts.append(delta["content"])
                                except Exception:
                                    pass
                    content = "".join(content_parts)
                else:
                    # Standard JSON response
                    text = raw_text
                    if "data: [DONE]" in text:
                        text = text.split("data: [DONE]")[0].strip()
                    try:
                        data = json.loads(text)
                    except Exception:
                        data = response.json()

                    content = data["choices"][0]["message"]["content"]
                    model_used = data.get("model", self.model)
                    usage = data.get("usage", usage)

                return {
                    "content": content,
                    "provider": "llm",
                    "model": model_used,
                    "usage": usage,
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "is_fallback": False,
                }
        except Exception as e:
            logger.error(f"LLM Provider error: {str(e)}. Triggering fallback.")
            from app.services.fallback_service import FallbackService
            fb = FallbackService.get_fallback_response(layer or "l1")
            return {
                "content": fb.get("content", "Halo! Layanan AI kami sedang dalam pemeliharaan berkala."),
                "provider": "fallback",
                "model": "fallback-safe",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": int((time.time() - start_time) * 1000),
                "is_fallback": True,
                "error_message": str(e),
                "handoff_url": fb.get("handoff_url"),
            }

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        layer: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        """Streaming generator yielding string token chunks as they arrive from LLM."""
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        if self.provider == "mock":
            sample_words = "Halo! Saya AI Assistant resmi D-KREASI. Ada yang bisa saya bantu terkait layanan kreasi kami?".split(" ")
            for w in sample_words:
                yield f"{w} "
                await asyncio.sleep(0.04)
            return

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        import json
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if line.startswith("data:") and not line.startswith("data: [DONE]"):
                            chunk_str = line[5:].strip()
                            if chunk_str:
                                try:
                                    chunk_json = json.loads(chunk_str)
                                    delta = chunk_json.get("choices", [{}])[0].get("delta", {})
                                    token = delta.get("content")
                                    if token:
                                        yield token
                                except Exception:
                                    pass
        except Exception as e:
            logger.error(f"Streaming error: {e}. Falling back to safe message.")
            from app.services.fallback_service import FallbackService
            fb = FallbackService.get_fallback_response(layer or "l1")
            yield fb.get("content", "Layanan asisten AI sedang dalam optimalisasi koneksi. Silakan hubungi CS kami.")
