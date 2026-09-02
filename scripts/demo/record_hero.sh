#!/usr/bin/env bash
# Record hero.gif using vhs if available, else fall back to Pillow placeholder.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if command -v vhs >/dev/null 2>&1; then
  vhs scripts/demo/hero.tape
else
  echo "vhs not found — generating placeholder GIF with Pillow"
  python3 scripts/demo/render_hero.py
fi
