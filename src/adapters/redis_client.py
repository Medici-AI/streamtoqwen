#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional
import json

import redis


class RedisClient:
    def __init__(self, url: Optional[str]) -> None:
        self._enabled = bool(url)
        self._client: Optional[redis.Redis] = None
        if self._enabled:
            # decode_responses ensures we get strings back
            self._client = redis.from_url(url, decode_responses=True)

    @property
    def enabled(self) -> bool:
        return self._enabled and self._client is not None

    def hset_json(self, key: str, field: str, value: dict) -> None:
        if not self.enabled:
            return
        self._client.hset(key, field, json.dumps(value))

    def hget_json(self, key: str, field: str) -> Optional[dict]:
        if not self.enabled:
            return None
        raw = self._client.hget(key, field)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def delete(self, key: str) -> None:
        if not self.enabled:
            return
        self._client.delete(key)


