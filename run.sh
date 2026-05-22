#!/usr/bin/env bash
set -euo pipefail

# Replit runtime entrypoint.
# Replit should run: python src/app.py (as requested).
export PORT="${PORT:-5000}"
export FLASK_DEBUG="${FLASK_DEBUG:-0}"

python src/app.py
