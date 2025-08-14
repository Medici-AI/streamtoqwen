#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Message:
    session_id: str
    timestamp: datetime
    sender: str  # "rm" or "customer"
    text: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationWindow:
    session_id: str
    window_start: datetime
    window_end: datetime
    messages: List[Message]

    def to_prompt(self) -> str:
        parts = [
            f"Window {self.window_start.isoformat()} - {self.window_end.isoformat()} (session {self.session_id})",
        ]
        for m in self.messages:
            parts.append(f"{m.timestamp.strftime('%H:%M:%S')} {m.sender.upper()}: {m.text}")
        return "\n".join(parts)
