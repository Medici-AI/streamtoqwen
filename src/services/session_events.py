#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from typing import Dict, Set

from starlette.websockets import WebSocket


class SessionBroadcaster:
    def __init__(self) -> None:
        self._subs: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, session_id: str, ws: WebSocket) -> None:
        async with self._lock:
            self._subs.setdefault(session_id, set()).add(ws)

    async def unsubscribe(self, session_id: str, ws: WebSocket) -> None:
        async with self._lock:
            if session_id in self._subs and ws in self._subs[session_id]:
                self._subs[session_id].remove(ws)
                if not self._subs[session_id]:
                    del self._subs[session_id]

    async def broadcast_json(self, session_id: str, payload: dict) -> None:
        targets: Set[WebSocket] = set()
        async with self._lock:
            if session_id in self._subs:
                targets = set(self._subs[session_id])
        for ws in list(targets):
            try:
                await ws.send_json(payload)
            except Exception:
                # Best-effort cleanup on failure
                try:
                    await self.unsubscribe(session_id, ws)
                except Exception:
                    pass
