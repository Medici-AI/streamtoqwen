#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..adapters.redis_client import RedisClient

from ..domain.conversation import Message, ConversationWindow
from ..domain.identity import RMIdentity


class IngestionService:
    def __init__(self, window_size_seconds: float = 4.0, redis_client: Optional[RedisClient] = None) -> None:
        self.window_size_seconds = window_size_seconds
        self._buffers: Dict[str, List[Message]] = defaultdict(list)
        self._redis = redis_client

    def _key(self, session_id: str) -> str:
        return f"ingestion:buffers:{session_id}"

    def _serialize(self, msgs: List[Message]) -> List[Dict[str, object]]:
        return [
            {
                "session_id": m.session_id,
                "timestamp": m.timestamp.isoformat(),
                "sender": m.sender,
                "text": m.text,
                "metadata": m.metadata,
            }
            for m in msgs
        ]

    def _deserialize(self, raw: List[Dict[str, object]]) -> List[Message]:
        out: List[Message] = []
        for d in raw or []:
            ts = d.get("timestamp")
            ts_dt = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
            out.append(
                Message(
                    session_id=d.get("session_id", ""),
                    timestamp=ts_dt,
                    sender=str(d.get("sender", "")),
                    text=str(d.get("text", "")),
                    metadata=d.get("metadata"),
                )
            )
        return out

    def _get_msgs(self, session_id: str) -> List[Message]:
        if self._redis and self._redis.enabled:
            data = self._redis.hget_json(self._key(session_id), "messages") or []
            return self._deserialize(data)
        return self._buffers[session_id]

    def _set_msgs(self, session_id: str, msgs: List[Message]) -> None:
        if self._redis and self._redis.enabled:
            self._redis.hset_json(self._key(session_id), "messages", self._serialize(msgs))
            return
        self._buffers[session_id] = msgs

    def add_event(self, event: Message) -> Tuple[bool, Optional[ConversationWindow]]:
        """Add a message event; if a window closes, return the ConversationWindow.
        Returns (closed, window). If no window closed, window is None.
        """
        msgs = self._get_msgs(event.session_id)
        msgs.append(event)

        timestamps = [m.timestamp for m in msgs]
        if not timestamps:
            return False, None
        min_time = min(timestamps)
        max_time = max(timestamps)
        span = (max_time - min_time).total_seconds()

        if span >= self.window_size_seconds:
            window = ConversationWindow(
                session_id=event.session_id,
                window_start=min_time,
                window_end=max_time,
                messages=list(msgs),
            )
            self._set_msgs(event.session_id, [])
            return True, window
        # Persist the updated buffer when window does not close yet
        self._set_msgs(event.session_id, msgs)
        return False, None

    def flush(self, session_id: str) -> Optional[ConversationWindow]:
        msgs = self._get_msgs(session_id)
        if not msgs:
            return None
        min_time = min(m.timestamp for m in msgs)
        max_time = max(m.timestamp for m in msgs)
        window = ConversationWindow(
            session_id=session_id,
            window_start=min_time,
            window_end=max_time,
            messages=list(msgs),
        )
        self._set_msgs(session_id, [])
        return window
