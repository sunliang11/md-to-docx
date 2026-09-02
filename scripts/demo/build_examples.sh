#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/scripts${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"

PRESET_MAP=(
  "technical-report:technical"
  "business-report:business"
  "academic-paper:academic"
  "api-document:technical"
  "meeting-notes:report"
  "ai-report:professional"
  "chinese-report:professional"
)

for entry in "${PRESET_MAP[@]}"; do
  dir="${entry%%:*}"
  preset="${entry##*:}"
  echo "Converting examples/${dir}/example.md [--preset ${preset}] ..."
  python3 -m md_to_docx "examples/${dir}/example.md" --preset "${preset}"
done
echo "Done: $(find examples -name example.docx | wc -l | tr -d ' ') docx files"
