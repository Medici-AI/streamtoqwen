#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta

from src.domain.conversation import Message
from src.services.ingestion_service import IngestionService


def test_window_closes_after_span() -> None:
    ing = IngestionService(window_size_seconds=2.0)
    base = datetime.utcnow()

    closed, res = ing.add_event(Message(session_id="s1", timestamp=base, sender="customer", text="hi"))
    assert closed is False and res is None

    # within window
    closed, res = ing.add_event(Message(session_id="s1", timestamp=base + timedelta(seconds=1), sender="rm", text="hello"))
    assert closed is False and res is None

    # exceed span
    closed, res = ing.add_event(Message(session_id="s1", timestamp=base + timedelta(seconds=2, milliseconds=10), sender="customer", text="more"))
    assert closed is True
    assert res is not None
    assert res.session_id == "s1"
