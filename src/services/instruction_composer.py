#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any
from ..domain.identity import RMIdentity


def compose_instruction(identity: RMIdentity, agent_results: Dict[str, Any]) -> Dict[str, Any]:
    # Extract light cues from agent_results (stable keys assumed)
    # Keep business behavior same: produce guidance, not alter core logic
    intent = _find_text(agent_results, "intent")
    sentiment = _find_text(agent_results, "sentiment")
    strategy = _find_text(agent_results, "strategy")
    decision = _find_text(agent_results, "decision")

    tone = "professional, empathetic" if identity.engagement.rapport >= 0.6 else "neutral"
    pacing = "measured" if identity.behavior.pacing >= 0.6 else "brisk"

    instruction_text = (
        f"Adopt a {tone} tone and {pacing} pacing. Focus on the customer's stated intent. "
        f"Acknowledge emotion, then propose next best action aligned with the strategic objective."
    )

    hints = {
        "voice_tone": tone,
        "pacing": pacing,
        "objective_focus": identity.strategy.objective,
        "next_best_action": decision or strategy or intent,
        "emotional_ack": sentiment[:120] if sentiment else None,
    }

    return {"instruction_text": instruction_text, "hints": hints}


def _find_text(agent_results: Dict[str, Any], role: str) -> str | None:
    try:
        for r in agent_results.get("results", []):
            if r.get("role") == role:
                return r.get("text")
    except Exception:
        pass
    return None
