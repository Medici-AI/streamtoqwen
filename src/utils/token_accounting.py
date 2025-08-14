#!/usr/bin/env python3
from __future__ import annotations

from typing import Tuple

# Rough heuristic: 1 token ≈ 4 chars (English)


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 4))


def merge_token_usage(input_tokens: int, output_tokens: int) -> Tuple[int, int, int]:
    total = input_tokens + output_tokens
    return input_tokens, output_tokens, total
