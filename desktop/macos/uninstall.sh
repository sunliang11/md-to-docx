#!/usr/bin/env bash
# Remove Finder Services installed by desktop/macos/install.sh.
set -euo pipefail

CONF_DIR="${HOME}/Library/Application Support/md-to-docx"
SERVICES_DIR="${HOME}/Library/Services"

CONVERT_NAME="Convert to Word (md-to-docx)"
REVERSE_NAME="Reverse to Markdown (md-to-docx)"

disable_service() {
  local display_name="$1"
  # Keys include literal double quotes; PlistBuddy needs them quoted.
  local key="\"(null) - ${display_name} - runWorkflowAsService\""
  /usr/libexec/PlistBuddy -c "Delete :NSServicesStatus:${key}" \
    "${HOME}/Library/Preferences/pbs.plist" 2>/dev/null || true
}

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "error: macOS only" >&2
  exit 1
fi

rm -rf "${SERVICES_DIR}/${CONVERT_NAME}.workflow"
rm -rf "${SERVICES_DIR}/${REVERSE_NAME}.workflow"
rm -f "${CONF_DIR}/runner.sh"
rm -f "${CONF_DIR}/context-menu.conf"

# Remove config dir if empty
if [[ -d "$CONF_DIR" ]] && [[ -z "$(ls -A "$CONF_DIR" 2>/dev/null || true)" ]]; then
  rmdir "$CONF_DIR" 2>/dev/null || true
fi

disable_service "$CONVERT_NAME"
disable_service "$REVERSE_NAME"
/System/Library/CoreServices/pbs -flush 2>/dev/null || true
/System/Library/CoreServices/pbs -update 2>/dev/null || true
killall Finder 2>/dev/null || true

echo "Removed Finder Services for md-to-docx."
echo "(CLI package itself was not uninstalled.)"
