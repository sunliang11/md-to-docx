#!/usr/bin/env bash
# md-to-docx Finder Services runner.
# Usage: runner.sh convert|reverse <file> [file...]
set -euo pipefail

CONF_DIR="${HOME}/Library/Application Support/md-to-docx"
CONF_FILE="${CONF_DIR}/context-menu.conf"
LOG_DIR="${HOME}/Library/Logs/md-to-docx"
LOG_FILE="${LOG_DIR}/context-menu.log"

log_line() {
  mkdir -p "$LOG_DIR" 2>/dev/null || true
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG_FILE" 2>/dev/null || true
}

notify() {
  local title="$1"
  local message="$2"
  /usr/bin/osascript -e "display notification \"${message//\"/\\\"}\" with title \"${title//\"/\\\"}\"" 2>/dev/null || true
}

alert() {
  local title="$1"
  local message="$2"
  /usr/bin/osascript -e "display alert \"${title//\"/\\\"}\" message \"${message//\"/\\\"}\" as warning" 2>/dev/null || true
}

die_notify() {
  log_line "ERROR: $1"
  notify "md-to-docx" "$1"
  alert "md-to-docx" "$1"
  echo "error: $1" >&2
  exit 1
}

load_conf() {
  CLI=""
  PRESET="technical"
  EXTRA_ARGS=""
  if [[ -f "$CONF_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CONF_FILE"
  fi
  if [[ -n "${MD_TO_DOCX_CLI:-}" ]]; then
    CLI="$MD_TO_DOCX_CLI"
  fi
  if [[ -z "$CLI" ]]; then
    die_notify "CLI path missing. Re-run: bash desktop/macos/install.sh (or set MD_TO_DOCX_CLI)"
  fi
  if [[ "$CLI" == *"/shims/"* ]]; then
    die_notify "CLI is a pyenv shim (Finder cannot run it). Re-run: bash desktop/macos/install.sh"
  fi
  if [[ ! -x "$CLI" ]] && ! command -v "$CLI" >/dev/null 2>&1; then
    die_notify "CLI not found: ${CLI}. Re-run install or set MD_TO_DOCX_CLI"
  fi
}

# Automator may pass file:// URLs instead of POSIX paths.
normalize_path() {
  local raw="$1"
  local out=""
  if [[ "$raw" == file://* ]]; then
    if command -v python3 >/dev/null 2>&1; then
      out="$(python3 -c 'import sys; from urllib.parse import unquote, urlparse; u=urlparse(sys.argv[1]); print(unquote(u.path))' "$raw" 2>/dev/null || true)"
    fi
    if [[ -z "$out" ]]; then
      out="${raw#file://}"
      out="${out%%\?*}"
      # Minimal %XX decode for common cases (space, non-ASCII left as-is if python missing).
      out="${out//%20/ }"
    fi
  else
    out="$raw"
  fi
  # Strip trailing slash (except root).
  if [[ "$out" != "/" && "$out" == */ ]]; then
    out="${out%/}"
  fi
  printf '%s\n' "$out"
}

ACTION="${1:-}"
shift || true

log_line "START action=${ACTION} argc=$# args=$*"

if [[ "$ACTION" != "convert" && "$ACTION" != "reverse" ]]; then
  die_notify "Usage: runner.sh convert|reverse <file>..."
fi

if [[ "$#" -lt 1 ]]; then
  die_notify "No files selected"
fi

load_conf

ok=0
fail=0
declare -a fail_names=()

for raw in "$@"; do
  [[ -z "$raw" ]] && continue
  f="$(normalize_path "$raw")"
  if [[ ! -f "$f" ]]; then
    fail=$((fail + 1))
    fail_names+=("$(basename "$f") (missing)")
    continue
  fi

  base="$(basename "$f")"
  ext="${base##*.}"
  ext_lc="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"

  if [[ "$ACTION" == "convert" ]]; then
    if [[ "$ext_lc" != "md" && "$ext_lc" != "markdown" ]]; then
      fail=$((fail + 1))
      fail_names+=("${base} (not .md)")
      continue
    fi
    # shellcheck disable=SC2086
    if "$CLI" "$f" --preset "$PRESET" $EXTRA_ARGS; then
      ok=$((ok + 1))
    else
      fail=$((fail + 1))
      fail_names+=("$base")
    fi
  else
    if [[ "$ext_lc" != "docx" ]]; then
      fail=$((fail + 1))
      fail_names+=("${base} (not .docx)")
      continue
    fi
    if "$CLI" reverse "$f"; then
      ok=$((ok + 1))
    else
      fail=$((fail + 1))
      fail_names+=("$base")
    fi
  fi
done

if [[ "$fail" -eq 0 ]]; then
  if [[ "$ACTION" == "convert" ]]; then
    msg="Converted ${ok} file(s) to Word"
  else
    msg="Reversed ${ok} file(s) to Markdown"
  fi
  log_line "OK: ${msg}"
  notify "md-to-docx" "$msg"
  exit 0
fi

summary="ok=${ok} fail=${fail}"
if [[ "${#fail_names[@]}" -gt 0 ]]; then
  summary="${summary}: ${fail_names[*]}"
fi
log_line "FAIL: ${summary}"
notify "md-to-docx failed" "$summary"
alert "md-to-docx failed" "$summary"$'\n'"See ${LOG_FILE}"
exit 1
