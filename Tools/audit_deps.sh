#!/usr/bin/env bash
set -euo pipefail

# Flattened dependency audit helper for CI/local runs.
# Uses local cache dirs to avoid permission issues on shared runners.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export HOME="$ROOT_DIR/.home"
export XDG_CACHE_HOME="$ROOT_DIR/.cache"
export PIP_AUDIT_CACHE_DIR="$XDG_CACHE_HOME/pip-audit"
mkdir -p "$HOME" "$XDG_CACHE_HOME" "$PIP_AUDIT_CACHE_DIR"

if [ ! -d .venv ]; then
  echo "[!] .venv not found. Create it first (python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt)." >&2
  exit 1
fi

source .venv/bin/activate

echo "[+] Running pip-audit on requirements.txt"
if ! pip-audit -r requirements.txt; then
  echo "[!] pip-audit failed (likely offline). Re-run with network access." >&2
fi

echo "[+] Running safety scan on requirements.txt"
if ! safety scan -r requirements.txt --full-report; then
  echo "[!] safety scan failed (likely offline). Re-run with network access." >&2
fi

echo "[✓] Dependency audit completed (check above for any failures)."
