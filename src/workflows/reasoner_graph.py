#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from typing import Dict, Any, List

from ..domain.conversation import ConversationWindow
from ..domain.identity import RMIdentity
from ..adapters.openai_client import OpenAIClient
from ..adapters.langsmith_client import traced_run
from ..utils.token_accounting import merge_token_usage, estimate_tokens
from ..services.vector_service import VectorService


class ReasonerGraph:
    def __init__(self) -> None:
        self.llm = OpenAIClient()
        self.vectors = VectorService()

    def _augment_with_retrieval(self, user: str) -> str:
        try:
            matches = self.vectors.retrieve_context(user, top_k=3)
            if not matches:
                return user
            snippets: List[str] = []
            for m in matches:
                md = m.get("metadata") or {}
                # Pinecone SDK variants; normalize best-effort
                score = m.get("score") or m.get("values") or ""
                snippets.append(f"[CTX session={md.get('session_id','?')} score={score}]")
            return user + "\n\nRetrieved Context:\n" + "\n".join(snippets)
        except Exception:
            return user

    async def _agent(self, role: str, system: str, user: str) -> Dict[str, Any]:
        with traced_run(name=f"agent:{role}", metadata={"role": role}):
            result = self.llm.chat_complete(system=system, user=user)
            return {
                "role": role,
                "text": result.text,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
            }

    async def run_window(self, window: ConversationWindow, identity: RMIdentity) -> Dict[str, Any]:
        base_user = window.to_prompt()
        # Retrieval-augmented user prompt
        user = self._augment_with_retrieval(base_user)
        system = identity.to_system_prompt()

        # Upsert window and identity in the background (best-effort)
        try:
            self.vectors.upsert_window(window)
            self.vectors.upsert_identity(window.session_id, identity)
        except Exception:
            pass

        # Run heads concurrently
        tasks = [
            self._agent("intent", system, user),
            self._agent("sentiment", system, user),
            self._agent("strategy", system, user),
            self._agent("learning", system, user),
            self._agent("decision", system, user),
        ]
        results = await asyncio.gather(*tasks)

        # Aggregate
        total_in = sum(r["input_tokens"] for r in results)
        total_out = sum(r["output_tokens"] for r in results)
        _, _, total = merge_token_usage(total_in, total_out)
        return {
            "session_id": window.session_id,
            "results": results,
            "tokens": {"input": total_in, "output": total_out, "total": total},
        }
