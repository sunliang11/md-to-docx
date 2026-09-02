#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/scripts${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"
for d in examples/*/ ; do
  echo "Converting ${d}example.md ..."
  python3 -m md_to_docx "${d}example.md"
done
echo "Done: $(find examples -name example.docx | wc -l | tr -d ' ') docx files"
