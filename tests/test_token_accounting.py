#!/usr/bin/env python3
from __future__ import annotations

from src.utils.token_accounting import estimate_tokens, merge_token_usage


def test_estimate_tokens_basic() -> None:
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("a" * 40) == 10


def test_merge_token_usage() -> None:
    i, o, t = merge_token_usage(10, 15)
    assert i == 10
    assert o == 15
    assert t == 25
