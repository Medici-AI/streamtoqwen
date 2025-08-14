#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from typing import Dict, Any

from ..domain.conversation import ConversationWindow
from ..domain.identity import RMIdentity
from ..workflows.reasoner_graph import ReasonerGraph


class ReasonerService:
    def __init__(self) -> None:
        self.graph = ReasonerGraph()

    async def analyze_window(self, window: ConversationWindow, identity: RMIdentity) -> Dict[str, Any]:
        return await self.graph.run_window(window, identity)
