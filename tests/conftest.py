#!/usr/bin/env python3
import os
import sys

# Ensure 'src' package is importable when running tests from repo root
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
