#!/usr/bin/env python3
from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Any, Iterator

from ..infrastructure.settings import load_settings

try:
    import langsmith as ls  # type: ignore
except Exception:  # pragma: no cover
    ls = None  # type: ignore


@contextmanager
def traced_run(name: str, metadata: Dict[str, Any] | None = None) -> Iterator[None]:
    s = load_settings()
    if not (ls and s.langsmith_api_key):
        yield
        return
    client = ls.Client(api_key=s.langsmith_api_key, project=s.langsmith_project)
    run = client.create_run(name=name, inputs=metadata or {})
    try:
        yield
        client.update_run(run["id"], outputs={"status": "ok"})
    except Exception as e:  # pragma: no cover
        client.update_run(run["id"], outputs={"status": "error", "error": str(e)})
        raise
