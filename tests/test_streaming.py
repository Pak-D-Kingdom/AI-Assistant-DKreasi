import pytest
import json
from app.core.context import RequestContext
from app.pipeline.orchestrator import PipelineOrchestrator


@pytest.mark.asyncio
async def test_execute_stream_yields_meta_and_tokens():
    orchestrator = PipelineOrchestrator()
    context = RequestContext(
        site_id="site_webia_1",
        site_name="WEBIA Business",
        layer="l3_webia",
        api_key_hash="hash",
    )
    messages = [{"role": "user", "content": "Halo, tes streaming"}]

    events = []
    async for event in orchestrator.execute_stream(messages=messages, context=context):
        assert event.startswith("data: ")
        raw_json = event[6:].strip()
        data = json.loads(raw_json)
        events.append(data)

    # First event must be meta with routing and session_id
    assert events[0]["type"] == "meta"
    assert "session_id" in events[0]
    assert events[0]["layer"] == "l3_webia"

    # Must contain token events
    token_events = [e for e in events if e.get("type") == "token"]
    assert len(token_events) > 0

    # Last event must be done
    assert events[-1]["type"] == "done"
