#!/usr/bin/env bash
set -euo pipefail

LOG=/tmp/md-to-docx-playground.log
HEALTH=http://127.0.0.1:8080/healthz

if curl -sf "$HEALTH" >/dev/null 2>&1; then
  echo "md-to-docx Playground already running on port 8080."
  exit 0
fi

echo "Starting md-to-docx Playground on port 8080…"
nohup python -m uvicorn web.app:app --host 0.0.0.0 --port 8080 \
  >"$LOG" 2>&1 &

for _ in $(seq 1 30); do
  if curl -sf "$HEALTH" >/dev/null 2>&1; then
    echo "Playground ready at port 8080 (Ports → Web Playground if the browser did not open)."
    exit 0
  fi
  sleep 1
done

echo "Playground failed to become healthy within 30s. Last log lines:" >&2
tail -n 40 "$LOG" >&2 || true
exit 1
