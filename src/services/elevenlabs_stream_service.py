#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any
from datetime import datetime
import asyncio
import logging

from ..adapters.elevenlabs_client import ElevenLabsClient
from ..services.ingestion_service import IngestionService
from ..domain.conversation import Message

logger = logging.getLogger(__name__)


class ElevenLabsStreamService:
    def __init__(self, ingestion: IngestionService) -> None:
        self.client = ElevenLabsClient()
        self.ingestion = ingestion

    async def start(self) -> None:
        await self.client.connect()
        self.client.on_transcript(self._handle_transcript)
        self.client.on_metadata(self._handle_metadata)
        # audio callback optional

    def _handle_transcript(self, evt: Dict[str, Any]) -> None:
        try:
            session_id = evt.get("session_id") or f"el_{int(datetime.utcnow().timestamp())}"
            ts = evt.get("timestamp")
            if isinstance(ts, str):
                timestamp = datetime.fromisoformat(ts)
            else:
                timestamp = ts or datetime.utcnow()
            sender = evt.get("sender", "customer")
            text = evt.get("text", "")
            metadata = evt.get("metadata")
            msg = Message(session_id=session_id, timestamp=timestamp, sender=sender, text=text, metadata=metadata)
            self.ingestion.add_event(msg)
        except Exception as e:
            logger.error("Error handling transcript: %s", e)

    def _handle_metadata(self, meta: Dict[str, Any]) -> None:
        # Can be used to enrich future messages; for now we attach per transcript event
        logger.debug("ElevenLabs metadata: %s", meta)
