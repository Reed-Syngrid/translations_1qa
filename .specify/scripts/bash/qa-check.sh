#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

echo "[qa-check] Running lint and tests..."

if command -v python >/dev/null 2>&1; then
  python -m ruff check .
  python -m pytest -q
else
  echo "[qa-check] Python is not available in PATH."
  exit 1
fi

echo "[qa-check] PASS"

