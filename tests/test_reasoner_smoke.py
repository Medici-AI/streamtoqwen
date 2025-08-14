#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta
import pytest

from src.domain.conversation import Message, ConversationWindow
from src.domain.identity import RMIdentity
from src.services.reasoner_service import ReasonerService


@pytest.mark.asyncio
async def test_reasoner_smoke() -> None:
    reasoner = ReasonerService()
    now = datetime.utcnow()
    window = ConversationWindow(
        session_id="s1",
        window_start=now,
        window_end=now + timedelta(seconds=2),
        messages=[
            Message(session_id="s1", timestamp=now, sender="customer", text="Hi, I want to refinance."),
            Message(session_id="s1", timestamp=now, sender="rm", text="Sure, I can help.")
        ],
    )
    identity = RMIdentity()
    result = await reasoner.analyze_window(window, identity)
    assert result["session_id"] == "s1"
    assert result["tokens"]["total"] >= 1
