#!/usr/bin/env python3
from __future__ import annotations

from typing import Callable, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    def __init__(self) -> None:
        self._connected = False
        self._on_transcript: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_metadata: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_audio: Optional[Callable[[bytes], None]] = None

    async def connect(self) -> None:
        # Placeholder: integrate SDK/WebSocket here, or reuse simulation code wired in
        self._connected = True
        logger.info("ElevenLabs client connected (placeholder)")

    def on_transcript(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._on_transcript = cb

    def on_metadata(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._on_metadata = cb

    def on_audio(self, cb: Callable[[bytes], None]) -> None:
        self._on_audio = cb

    async def send_signal(self, session_id: str, payload: Dict[str, Any]) -> None:
        # Placeholder: send instruction back to ElevenLabs agent
        logger.info("Signal to ElevenLabs session %s: %s", session_id, payload)
