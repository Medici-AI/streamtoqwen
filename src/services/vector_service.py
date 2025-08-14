#!/usr/bin/env python3
from __future__ import annotations

from typing import List, Dict, Any

from ..adapters.openai_client import OpenAIClient
from ..adapters.vector_client import VectorClient
from ..domain.conversation import ConversationWindow
from ..domain.identity import RMIdentity


class VectorService:
    def __init__(self) -> None:
        self.llm = OpenAIClient()
        self.vdb = VectorClient(index_name="rm-mvp")

    def upsert_window(self, window: ConversationWindow) -> None:
        texts = [m.text for m in window.messages]
        if not texts:
            return
        # Concatenate for a single embedding per window (simple MVP)
        joined = "\n".join(texts)
        vec = self.llm.embed([joined])[0]
        self.vdb.upsert(ids=[f"win:{window.session_id}:{window.window_end.isoformat()}"], vectors=[vec], metadata=[{"session_id": window.session_id}])

    def upsert_identity(self, session_id: str, identity: RMIdentity) -> None:
        text = identity.to_system_prompt()
        vec = self.llm.embed([text])[0]
        self.vdb.upsert(ids=[f"id:{session_id}"], vectors=[vec], metadata=[{"session_id": session_id, "type": "identity"}])

    def retrieve_context(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        vec = self.llm.embed([text])[0]
        matches = self.vdb.query(vec, top_k=top_k)
        return matches
