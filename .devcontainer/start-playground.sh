#!/usr/bin/env bash
if curl -sf http://127.0.0.1:8080/healthz >/dev/null 2>&1; then
  exit 0
fi
nohup uvicorn web.app:app --host 0.0.0.0 --port 8080 \
  > /tmp/md-to-docx-playground.log 2>&1 &
