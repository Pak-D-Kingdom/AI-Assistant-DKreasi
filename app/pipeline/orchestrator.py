import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.llm_service import LlmService
from app.services.rag_service import RagService
from app.services.guardrail_service import GuardrailService
from app.services.fallback_service import FallbackService
from app.services.usage_service import UsageService
from app.pipeline.tool_registry import ToolRegistry
from app.core.context import RequestContext


class PipelineOrchestrator:
    def __init__(
        self,
        llm_service: Optional[LlmService] = None,
        rag_service: Optional[RagService] = None,
        guardrail_service: Optional[GuardrailService] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ):
        self.llm_service = llm_service or LlmService()
        self.rag_service = rag_service or RagService()
        self.guardrail_service = guardrail_service or GuardrailService()
        self.tool_registry = tool_registry or ToolRegistry()

    async def execute(
        self,
        messages: List[Dict[str, str]],
        context: RequestContext,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        session_id = context.session_id or f"sess_{uuid.uuid4().hex[:12]}"
        layer_name = context.layer
        tenant_id = context.tenant_id

        latest_user_message = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )

        # 1. Guardrail Input Inspection
        input_check = self.guardrail_service.inspect_input(latest_user_message)
        if not input_check["safe"]:
            denied_msg = "Maaf, saya tidak dapat memproses permintaan ini karena terindikasi melanggar batasan keamanan sistem."
            if db:
                await UsageService.log_interaction(
                    db=db,
                    session_id=session_id,
                    layer=layer_name,
                    user_message=latest_user_message,
                    assistant_message=denied_msg,
                    tenant_id=tenant_id,
                    site_id=context.site_id,
                    provider="guardrail",
                    model="guardrail-v1",
                    is_fallback=True,
                )
            return {
                "success": True,
                "layer": layer_name,
                "message": {"role": "assistant", "content": denied_msg},
                "routing": None,
                "meta": {"guardrail_blocked": True},
            }

        # 2. Intent Detection & Routing (Layer specific)
        layer_handler = self.tool_registry.get_layer(layer_name)
        routing_payload = layer_handler.route_intent(latest_user_message)

        # 3. Knowledge Retrieval (RAG)
        retrieved_chunks = self.rag_service.search(
            query=latest_user_message,
            layer=layer_name,
            tenant_id=tenant_id,
            top_k=3,
        )
        rag_context = self.rag_service.format_context(retrieved_chunks)

        # 4. Construct System Prompt
        base_prompt = layer_handler.get_system_prompt()
        final_system_prompt = f"{base_prompt}\n\n{rag_context}" if rag_context else base_prompt

        # 5. Call LLM
        llm_response = await self.llm_service.chat(
            messages=messages,
            system_prompt=final_system_prompt,
        )

        # 6. Guardrail Output Inspection
        raw_output = llm_response["content"]
        sanitized_output = self.guardrail_service.inspect_output(layer_name, raw_output)

        # 7. DB Logging
        if db:
            usage_data = llm_response.get("usage", {})
            await UsageService.log_interaction(
                db=db,
                session_id=session_id,
                layer=layer_name,
                user_message=latest_user_message,
                assistant_message=sanitized_output,
                tenant_id=tenant_id,
                site_id=context.site_id,
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                latency_ms=llm_response.get("latency_ms", 0),
                provider=llm_response.get("provider", "llm"),
                model=llm_response.get("model", "default"),
                is_fallback=llm_response.get("is_fallback", False),
            )

        return {
            "success": True,
            "layer": layer_name,
            "session_id": session_id,
            "message": {"role": "assistant", "content": sanitized_output},
            "routing": routing_payload,
            "meta": {
                "provider": llm_response.get("provider"),
                "model": llm_response.get("model"),
                "latency_ms": llm_response.get("latency_ms"),
                "retrieved_chunks": len(retrieved_chunks),
            },
        }
