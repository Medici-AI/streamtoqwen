#!/usr/bin/env python3
from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os

from ..infrastructure.settings import load_settings
from ..utils.token_accounting import estimate_tokens

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional at test time
    OpenAI = None  # type: ignore


@dataclass
class OpenAIResult:
    text: str
    input_tokens: int
    output_tokens: int


class OpenAIClient:
    def __init__(self, model_override: Optional[str] = None, embedding_model: Optional[str] = None) -> None:
        self.settings = load_settings()
        self.model = model_override or self.settings.openai_model
        self.embedding_model = embedding_model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self._client = None
        if OpenAI and self.settings.openai_api_key:
            self._client = OpenAI(api_key=self.settings.openai_api_key, organization=self.settings.openai_organization)

    def chat_complete(self, system: str, user: str, temperature: float = 0.4, max_tokens: int = 512) -> OpenAIResult:
        if self._client is None:
            # Mocked response for environments without API
            output_text = "[MOCK] Guidance based on context and RM identity."
            return OpenAIResult(
                text=output_text,
                input_tokens=estimate_tokens(system + "\n" + user),
                output_tokens=estimate_tokens(output_text),
            )

        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (resp.choices[0].message.content or "").strip()
        usage = resp.usage
        return OpenAIResult(
            text=text,
            input_tokens=getattr(usage, "prompt_tokens", 0),
            output_tokens=getattr(usage, "completion_tokens", 0),
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Safe mock
        if self._client is None:
            return [[0.0] * 1536 for _ in texts]
        resp = self._client.embeddings.create(model=self.embedding_model, input=texts)
        vectors = [d.embedding for d in resp.data]
        return vectors
