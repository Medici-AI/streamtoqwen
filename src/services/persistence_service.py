#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any
from datetime import datetime
from ..adapters.cosmos_client import CosmosAdapter
from ..domain.conversation import ConversationWindow


class PersistenceService:
    def __init__(self) -> None:
        self.cosmos = CosmosAdapter()

    def save_window(self, window: ConversationWindow) -> None:
        item = {
            "id": f"win::{window.session_id}::{int(window.window_end.timestamp())}",
            "session_id": window.session_id,
            "type": "window",
            "window_start": window.window_start.isoformat(),
            "window_end": window.window_end.isoformat(),
            "messages": [
                {"timestamp": m.timestamp.isoformat(), "sender": m.sender, "text": m.text, "metadata": m.metadata}
                for m in window.messages
            ],
        }
        self.cosmos.upsert(item)

    def save_result(self, session_id: str, result: Dict[str, Any]) -> None:
        item = {
            "id": f"res::{session_id}::{int(datetime.utcnow().timestamp())}",
            "session_id": session_id,
            "type": "result",
            "result": result,
            "ts": datetime.utcnow().isoformat(),
        }
        self.cosmos.upsert(item)
