#!/usr/bin/env bash
set -euo pipefail

# Load local env if present (do not commit .env)
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

export PYTHONPATH="$(pwd):${PYTHONPATH:-}"
exec uvicorn src.app.api_gateway:app --host 0.0.0.0 --port 8000 --reload
