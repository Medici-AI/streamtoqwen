#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from typing import Callable, Optional

from ..infrastructure.settings import load_settings

try:  # Optional dependency for local dev
    from azure.servicebus.aio import ServiceBusClient
    from azure.servicebus import ServiceBusMessage
except Exception:  # pragma: no cover
    ServiceBusClient = None  # type: ignore
    ServiceBusMessage = None  # type: ignore


class QueueClient:
    def __init__(self) -> None:
        self.settings = load_settings()
        self._client = None
        if ServiceBusClient and self.settings.azure_service_bus_conn:
            self._client = ServiceBusClient.from_connection_string(
                conn_str=self.settings.azure_service_bus_conn
            )

    async def publish(self, topic: Optional[str], body: dict) -> None:
        if self._client is None or ServiceBusMessage is None:
            # No-op in local environments without Azure configured
            return
        topic_name = topic or self.settings.azure_service_bus_topic
        # Pre-serialize to avoid datetime issues
        def _default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
        payload = json.dumps(body, default=_default)
        async with self._client:
            sender = self._client.get_topic_sender(topic_name=topic_name)  # type: ignore
            async with sender:
                msg = ServiceBusMessage(payload)  # type: ignore
                await sender.send_messages(msg)  # type: ignore

    async def consume_subscription(self, topic: Optional[str], subscription: Optional[str], handler: Callable[[dict], None]) -> None:
        if self._client is None:
            # No-op for local dev
            return
        topic_name = topic or self.settings.azure_service_bus_topic
        sub_name = subscription or self.settings.azure_service_bus_sub
        async with self._client:
            receiver = self._client.get_subscription_receiver(topic_name=topic_name, subscription_name=sub_name)  # type: ignore
            async with receiver:
                async for msg in receiver:  # type: ignore
                    try:
                        # Body is iterable of bytes for received messages
                        raw_bytes = b"".join(part if isinstance(part, (bytes, bytearray)) else bytes(part) for part in msg.body)  # type: ignore
                        data = json.loads(raw_bytes.decode("utf-8"))
                        handler(data)
                        await receiver.complete_message(msg)  # type: ignore
                    except Exception:
                        await receiver.abandon_message(msg)  # type: ignore
