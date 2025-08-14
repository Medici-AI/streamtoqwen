#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from azure.cosmos import CosmosClient, PartitionKey  # type: ignore
except Exception:  # pragma: no cover
    CosmosClient = None  # type: ignore
    PartitionKey = None  # type: ignore


class CosmosAdapter:
    def __init__(self, conn_str_env: str = "AZURE_COSMOS_CONNECTION", db_name: str = "rm_mvp", container_name: str = "sessions") -> None:
        self.conn_str = os.getenv(conn_str_env)
        self.db_name = db_name
        self.container_name = container_name
        self._client = None
        self._container = None
        if CosmosClient and self.conn_str:
            try:
                self._client = CosmosClient.from_connection_string(self.conn_str)
                self._ensure()
            except Exception as e:  # pragma: no cover
                logger.error("Cosmos initialization failed: %s", e)
                self._client = None

    def _ensure(self) -> None:
        if not self._client:
            return
        db = self._client.create_database_if_not_exists(id=self.db_name)
        self._container = db.create_container_if_not_exists(id=self.container_name, partition_key=PartitionKey(path="/session_id"))

    def upsert(self, item: Dict[str, Any]) -> None:
        if not self._container:
            return
        self._container.upsert_item(item)

    def read(self, session_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        if not self._container:
            return None
        try:
            return self._container.read_item(item=item_id, partition_key=session_id)
        except Exception:
            return None
