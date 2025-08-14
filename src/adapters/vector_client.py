#!/usr/bin/env python3
from __future__ import annotations

from typing import List, Tuple, Dict, Any
import os

from ..infrastructure.settings import load_settings

try:
    from pinecone import Pinecone, ServerlessSpec  # type: ignore
except Exception:  # pragma: no cover
    Pinecone = None  # type: ignore
    ServerlessSpec = None  # type: ignore


def _embedding_dim_from_env() -> int:
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").lower()
    return 3072 if "large" in model else 1536


def _default_index_name() -> str:
    return f"rm-mvp-{_embedding_dim_from_env()}"


class VectorClient:
    def __init__(self, index_name: str | None = None) -> None:
        self.settings = load_settings()
        self.dimension = _embedding_dim_from_env()
        self.index_name = index_name or _default_index_name()
        self._pc = None
        self._index = None
        api_key = self._get_api_key()
        if Pinecone and api_key:
            self._pc = Pinecone(api_key=api_key)
            self._ensure_index()

    def _get_api_key(self) -> str | None:
        return getattr(self.settings, "pinecone_api_key", None) or getenv_default("PINECONE_API_KEY")

    def _ensure_index(self) -> None:
        if self._pc is None:
            return
        # List existing indexes
        existing = {i.name for i in self._pc.list_indexes()}
        if self.index_name not in existing:
            # Create serverless index (defaults)
            cloud = os.getenv("PINECONE_CLOUD", "aws")
            region = os.getenv("PINECONE_REGION", "us-east-1")
            spec = ServerlessSpec(cloud=cloud, region=region) if ServerlessSpec else None
            if spec is not None:
                self._pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=spec,
                )
        self._index = self._pc.Index(self.index_name)

    def upsert(self, ids: List[str], vectors: List[List[float]], metadata: List[Dict[str, Any]] | None = None) -> None:
        if self._index is None:
            return
        items = []
        for idx, vec in zip(ids, vectors):
            md = None
            if metadata and len(metadata) == len(ids):
                md = metadata[ids.index(idx)]
            items.append({"id": idx, "values": vec, "metadata": md})
        self._index.upsert(vectors=items)

    def query(self, vector: List[float], top_k: int = 5, filter: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        if self._index is None:
            return []
        res = self._index.query(vector=vector, top_k=top_k, filter=filter or {})
        return [m.dict() if hasattr(m, "dict") else m for m in res.matches]


def getenv_default(key: str, default: str | None = None) -> str | None:
    import os
    return os.getenv(key, default)
