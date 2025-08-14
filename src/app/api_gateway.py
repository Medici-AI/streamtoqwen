#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ..domain.conversation import Message, ConversationWindow
from ..domain.identity import RMIdentity
from ..services.reasoner_service import ReasonerService
from ..workflows.rm_copy_graph import RMCopyGraph
from ..services.ingestion_service import IngestionService
from ..adapters.redis_client import RedisClient
from ..adapters.queue_client import QueueClient
from ..infrastructure.settings import load_settings
from ..services.instruction_composer import compose_instruction
from ..adapters.elevenlabs_client import ElevenLabsClient
from ..services.persistence_service import PersistenceService
from ..services.session_events import SessionBroadcaster

app = FastAPI(title="RM MVP API")

reasoner = ReasonerService()
rm_copy = RMCopyGraph()
redis_client = RedisClient(load_settings().redis_url)
ingestion = IngestionService(window_size_seconds=4.0, redis_client=redis_client)
queue_client = QueueClient()
settings = load_settings()
persist = PersistenceService()
bus = SessionBroadcaster()

elevenlabs_enabled = os.getenv("ELEVENLABS_ENABLED", "false").lower() in ("1", "true", "yes")
elevenlabs_client = ElevenLabsClient() if elevenlabs_enabled else None


class MessageIn(BaseModel):
    session_id: str
    timestamp: datetime
    sender: str
    text: str
    metadata: Optional[Dict[str, Any]] = None


class WindowIn(BaseModel):
    session_id: str
    window_start: datetime
    window_end: datetime
    messages: List[MessageIn]


@app.get("/session/{session_id}")
async def session_page(session_id: str) -> HTMLResponse:
    html = f"""
<!doctype html>
<html>
<head><meta charset='utf-8'><title>Session {session_id}</title></head>
<body>
<h2>Session {session_id}</h2>
<pre id='log'></pre>
<script>
const log = document.getElementById('log');
const ws = new WebSocket(`ws://${{location.host}}/ws/{session_id}`);
ws.onmessage = (ev) => {{
  try {{
    const data = JSON.parse(ev.data);
    log.textContent += JSON.stringify(data, null, 2) + '\n\n';
  }} catch (e) {{ log.textContent += ev.data + '\n'; }}
}};
</script>
</body>
</html>
"""
    return HTMLResponse(html)


@app.websocket("/ws/{session_id}")
async def session_ws(ws: WebSocket, session_id: str) -> None:
    await ws.accept()
    await bus.subscribe(session_id, ws)
    try:
        while True:
            await ws.receive_text()  # keepalive; client doesn't need to send
    except WebSocketDisconnect:
        await bus.unsubscribe(session_id, ws)


@app.post("/analyze/window")
async def analyze_window(window: WindowIn) -> Dict[str, Any]:
    domain_msgs = [Message(**m.model_dump()) for m in window.messages]
    w = ConversationWindow(
        session_id=window.session_id,
        window_start=window.window_start,
        window_end=window.window_end,
        messages=domain_msgs,
    )
    identity = RMIdentity()
    result = await reasoner.analyze_window(w, identity)
    persist.save_window(w)
    persist.save_result(w.session_id, result)
    await _maybe_send_elevenlabs_signal(w.session_id, identity, result)
    await bus.broadcast_json(w.session_id, {"type": "window_result", "window_end": w.window_end.isoformat(), "result": result})
    return result


class RMTurnIn(BaseModel):
    rm_turn: str


@app.post("/rm-copy/update")
async def rm_copy_update(payload: RMTurnIn) -> Dict[str, Any]:
    identity = RMIdentity()
    result = await rm_copy.update_identity(payload.rm_turn, identity)
    return result


@app.post("/ingest/event")
async def ingest_event(event: MessageIn) -> Dict[str, Any]:
    msg = Message(**event.model_dump())
    closed, window = ingestion.add_event(msg)
    if not closed or window is None:
        return {"window_closed": False, "result": None}
    try:
        identity = RMIdentity()
        result = await reasoner.analyze_window(window, identity)
        persist.save_window(window)
        persist.save_result(window.session_id, result)
        await _maybe_send_elevenlabs_signal(window.session_id, identity, result)
        await bus.broadcast_json(window.session_id, {"type": "window_result", "window_end": window.window_end.isoformat(), "result": result})
        return {"window_closed": True, "result": result}
    except Exception as e:
        return {"window_closed": True, "error": str(e)}


@app.post("/ingest/flush/{session_id}")
async def ingest_flush(session_id: str) -> Dict[str, Any]:
    window = ingestion.flush(session_id)
    if window is None:
        return {"flushed": False, "result": None}
    try:
        identity = RMIdentity()
        result = await reasoner.analyze_window(window, identity)
        persist.save_window(window)
        persist.save_result(session_id, result)
        await _maybe_send_elevenlabs_signal(session_id, identity, result)
        await bus.broadcast_json(session_id, {"type": "window_result", "window_end": window.window_end.isoformat(), "result": result})
        return {"flushed": True, "result": result}
    except Exception as e:
        return {"flushed": True, "error": str(e)}


@app.post("/ingest/publish")
async def ingest_publish(event: MessageIn) -> Dict[str, Any]:
    # Publish to Service Bus topic if configured
    await queue_client.publish(None, event.model_dump())
    return {"published": True}


@app.on_event("startup")
async def startup_consumer() -> None:
    # Optionally start a background consumer for Service Bus subscription
    if settings.azure_service_bus_conn and settings.azure_service_bus_topic and settings.azure_service_bus_sub:
        async def handler_loop():
            async def _handler(data: dict) -> None:
                try:
                    msg = Message(
                        session_id=data["session_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else data["timestamp"],
                        sender=data["sender"],
                        text=data["text"],
                    )
                    closed, window = ingestion.add_event(msg)
                    if closed and window is not None:
                        identity = RMIdentity()
                        await reasoner.analyze_window(window, identity)
                except Exception:
                    # Swallow to keep consumer alive in MVP
                    pass
            await queue_client.consume_subscription(None, None, lambda d: asyncio.create_task(_handler(d)))
        asyncio.create_task(handler_loop())

    if elevenlabs_enabled and elevenlabs_client:
        await elevenlabs_client.connect()

async def _maybe_send_elevenlabs_signal(session_id: str, identity: RMIdentity, agent_results: Dict[str, Any]) -> None:
    if not (elevenlabs_enabled and elevenlabs_client):
        return
    try:
        payload = compose_instruction(identity, agent_results)
        await elevenlabs_client.send_signal(session_id, payload)
    except Exception:
        pass
