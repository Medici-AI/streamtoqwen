#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any

from ..domain.identity import RMIdentity
from ..adapters.openai_client import OpenAIClient


class RMCopyGraph:
    def __init__(self) -> None:
        self.llm = OpenAIClient()

    def _build_prompt(self, rm_turn: str, prev_identity: RMIdentity) -> str:
        return (
            f"Analyze the following RM turn for emotional, cognitive, strategic, and engagement cues. "
            f"Return JSON with fields: behavior.adjustments, cognitive.adjustments, engagement.adjustments, strategy.notes.\n"
            f"Current Identity: {prev_identity.to_system_prompt()}\n"
            f"RM Turn: {rm_turn}"
        )

    async def update_identity(self, rm_turn: str, identity: RMIdentity) -> Dict[str, Any]:
        system = "You are an expert identity modeler following LIDA principles."
        user = self._build_prompt(rm_turn, identity)
        result = self.llm.chat_complete(system=system, user=user)
        # For MVP, return text; a real impl would parse and mutate identity safely
        return {"text": result.text, "input_tokens": result.input_tokens, "output_tokens": result.output_tokens}
