#!/usr/bin/env bash
# Install Finder Services (context menu) for md-to-docx (current user only).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_RUNNER="${SCRIPT_DIR}/lib/runner.sh"

CONF_DIR="${HOME}/Library/Application Support/md-to-docx"
CONF_FILE="${CONF_DIR}/context-menu.conf"
RUNNER_DST="${CONF_DIR}/runner.sh"
SERVICES_DIR="${HOME}/Library/Services"

CONVERT_NAME="Convert to Word (md-to-docx)"
REVERSE_NAME="Reverse to Markdown (md-to-docx)"

is_shim_path() {
  [[ "$1" == *"/shims/"* ]]
}

find_pyenv_bin() {
  local root="${PYENV_ROOT:-$HOME/.pyenv}"
  local c
  for c in \
    /opt/homebrew/bin/pyenv \
    /usr/local/bin/pyenv \
    "${root}/bin/pyenv"
  do
    if [[ -x "$c" ]]; then
      printf '%s\n' "$c"
      return 0
    fi
  done
  if command -v pyenv >/dev/null 2>&1; then
    # May be a shell function; only accept if it resolves to an executable file.
    c="$(command -v pyenv 2>/dev/null || true)"
    if [[ -n "$c" && -x "$c" && "$c" != "pyenv" ]]; then
      printf '%s\n' "$c"
      return 0
    fi
  fi
  return 1
}

# Prefer versions/<ver>/bin/md-to-docx under PYENV_ROOT (never shims).
resolve_from_pyenv_versions() {
  local root="${PYENV_ROOT:-$HOME/.pyenv}"
  local preferred=""
  local ver_file="${root}/version"
  local pyenv_bin=""
  local ver=""

  pyenv_bin="$(find_pyenv_bin || true)"
  if [[ -n "$pyenv_bin" ]]; then
    ver="$("$pyenv_bin" version-name 2>/dev/null || true)"
  fi
  if [[ -z "$ver" && -f "$ver_file" ]]; then
    ver="$(tr -d '[:space:]' < "$ver_file")"
  fi
  if [[ -n "$ver" && "$ver" != "system" ]]; then
    preferred="${root}/versions/${ver}/bin/md-to-docx"
    if [[ -x "$preferred" ]]; then
      printf '%s\n' "$preferred"
      return 0
    fi
  fi

  local newest="" newest_mtime=0 path mtime
  shopt -s nullglob
  for path in "${root}/versions"/*/bin/md-to-docx; do
    [[ -x "$path" ]] || continue
    mtime="$(stat -f '%m' "$path" 2>/dev/null || stat -c '%Y' "$path" 2>/dev/null || echo 0)"
    if [[ "$mtime" -ge "$newest_mtime" ]]; then
      newest_mtime="$mtime"
      newest="$path"
    fi
  done
  shopt -u nullglob
  if [[ -n "$newest" ]]; then
    printf '%s\n' "$newest"
    return 0
  fi
  return 1
}

accept_cli_path() {
  local path="$1"
  if [[ -z "$path" ]]; then
    return 1
  fi
  if is_shim_path "$path"; then
    return 1
  fi
  if [[ -x "$path" ]]; then
    printf '%s\n' "$path"
    return 0
  fi
  return 1
}

resolve_cli() {
  local candidate="" pyenv_bin="" real=""

  if [[ -n "${MD_TO_DOCX_CLI:-}" ]]; then
    if accept_cli_path "$MD_TO_DOCX_CLI"; then
      return 0
    fi
    if command -v "$MD_TO_DOCX_CLI" >/dev/null 2>&1; then
      candidate="$(command -v "$MD_TO_DOCX_CLI")"
      if accept_cli_path "$candidate"; then
        return 0
      fi
    fi
    # Env pointed at a shim — keep resolving instead of failing immediately.
    if ! is_shim_path "${MD_TO_DOCX_CLI}" && [[ ! -x "${MD_TO_DOCX_CLI}" ]]; then
      echo "error: MD_TO_DOCX_CLI is set but not executable: $MD_TO_DOCX_CLI" >&2
      return 1
    fi
  fi

  # Homebrew / root pyenv binary (Finder has no zsh pyenv function).
  pyenv_bin="$(find_pyenv_bin || true)"
  if [[ -n "$pyenv_bin" ]]; then
    real="$("$pyenv_bin" which md-to-docx 2>/dev/null || true)"
    if accept_cli_path "$real"; then
      return 0
    fi
    # which returned a shim or empty — build versions/<ver>/bin path
    if resolve_from_pyenv_versions; then
      return 0
    fi
  else
    if resolve_from_pyenv_versions; then
      return 0
    fi
  fi

  if command -v md-to-docx >/dev/null 2>&1; then
    candidate="$(command -v md-to-docx)"
    if accept_cli_path "$candidate"; then
      return 0
    fi
    echo "error: md-to-docx on PATH is a pyenv shim (${candidate})." >&2
    echo "  Finder cannot run shims. Re-run after fixing, or set a real binary:" >&2
    echo "  export MD_TO_DOCX_CLI=\"\$HOME/.pyenv/versions/<ver>/bin/md-to-docx\"" >&2
    return 1
  fi

  echo "error: md-to-docx not found on PATH." >&2
  echo "  Install first: pip install -e .   (from the repo root)" >&2
  echo "  Or set: export MD_TO_DOCX_CLI=/absolute/path/to/md-to-docx" >&2
  return 1
}

write_workflow() {
  local display_name="$1"
  local action="$2"
  local send_types_xml="$3"
  local uuid_suffix="$4"
  local workflow_dir="${SERVICES_DIR}/${display_name}.workflow"
  local contents="${workflow_dir}/Contents"

  rm -rf "$workflow_dir"
  mkdir -p "$contents"

  # Escape for embedding in Automator COMMAND_STRING
  local runner_escaped
  runner_escaped="$(printf '%s' "$RUNNER_DST" | sed 's/\\/\\\\/g; s/"/\\"/g')"

  cat > "${contents}/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>com.md-to-docx.automator.${action}</string>
	<key>CFBundleName</key>
	<string>${display_name}</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleVersion</key>
	<string>1.0</string>
	<key>NSServices</key>
	<array>
		<dict>
			<key>NSMenuItem</key>
			<dict>
				<key>default</key>
				<string>${display_name}</string>
			</dict>
			<key>NSMessage</key>
			<string>runWorkflowAsService</string>
			<key>NSRequiredContext</key>
			<dict>
				<key>NSApplicationIdentifier</key>
				<string>com.apple.finder</string>
			</dict>
			<key>NSSendFileTypes</key>
			<array>
${send_types_xml}
			</array>
		</dict>
	</array>
	<key>UTImportedTypeDeclarations</key>
	<array>
		<dict>
			<key>UTTypeConformsTo</key>
			<array>
				<string>public.plain-text</string>
			</array>
			<key>UTTypeDescription</key>
			<string>Markdown</string>
			<key>UTTypeIdentifier</key>
			<string>net.daringfireball.markdown</string>
			<key>UTTypeTagSpecification</key>
			<dict>
				<key>public.filename-extension</key>
				<array>
					<string>md</string>
					<string>markdown</string>
				</array>
			</dict>
		</dict>
		<dict>
			<key>UTTypeConformsTo</key>
			<array>
				<string>public.data</string>
				<string>public.composite-content</string>
			</array>
			<key>UTTypeDescription</key>
			<string>Office Open XML Word Document</string>
			<key>UTTypeIdentifier</key>
			<string>org.openxmlformats.wordprocessingml.document</string>
			<key>UTTypeTagSpecification</key>
			<dict>
				<key>public.filename-extension</key>
				<array>
					<string>docx</string>
				</array>
				<key>public.mime-type</key>
				<array>
					<string>application/vnd.openxmlformats-officedocument.wordprocessingml.document</string>
				</array>
			</dict>
		</dict>
	</array>
</dict>
</plist>
EOF

  # Minimal Automator document: Run Shell Script with files as arguments.
  # Keys must match AMDefaultParameters in Run Shell Script.action (inputMethod/shell).
  cat > "${contents}/document.wflow" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AMApplicationBuild</key>
	<string>523</string>
	<key>AMApplicationVersion</key>
	<string>2.10</string>
	<key>AMDocumentVersion</key>
	<string>2</string>
	<key>actions</key>
	<array>
		<dict>
			<key>action</key>
			<dict>
				<key>AMAccepts</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Optional</key>
					<true/>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.path</string>
					</array>
				</dict>
				<key>AMActionVersion</key>
				<string>2.0.3</string>
				<key>AMApplication</key>
				<array>
					<string>Automator</string>
				</array>
				<key>AMParameterProperties</key>
				<dict>
					<key>COMMAND_STRING</key>
					<dict/>
					<key>CheckedForUserDefaultShell</key>
					<dict/>
					<key>inputMethod</key>
					<dict/>
					<key>shell</key>
					<dict/>
					<key>source</key>
					<dict/>
				</dict>
				<key>AMProvides</key>
				<dict>
					<key>Container</key>
					<string>List</string>
					<key>Types</key>
					<array>
						<string>com.apple.cocoa.string</string>
					</array>
				</dict>
				<key>ActionBundlePath</key>
				<string>/System/Library/Automator/Run Shell Script.action</string>
				<key>ActionName</key>
				<string>Run Shell Script</string>
				<key>ActionParameters</key>
				<dict>
					<key>COMMAND_STRING</key>
					<string>"${runner_escaped}" ${action} "\$@"</string>
					<key>CheckedForUserDefaultShell</key>
					<true/>
					<key>inputMethod</key>
					<integer>1</integer>
					<key>shell</key>
					<string>/bin/bash</string>
					<key>source</key>
					<string></string>
				</dict>
				<key>BundleIdentifier</key>
				<string>com.apple.RunShellScript</string>
				<key>CFBundleVersion</key>
				<string>2.0.3</string>
				<key>CanShowSelectedItemsWhenRun</key>
				<false/>
				<key>CanShowWhenRun</key>
				<true/>
				<key>Category</key>
				<array>
					<string>AMCategoryUtilities</string>
				</array>
				<key>Class Name</key>
				<string>RunShellScriptAction</string>
				<key>InputUUID</key>
				<string>A1B2C3D4-E5F6-7890-ABCD-000000000001</string>
				<key>Keywords</key>
				<array>
					<string>Shell</string>
					<string>Script</string>
					<string>Command</string>
					<string>Run</string>
					<string>Unix</string>
				</array>
				<key>OutputUUID</key>
				<string>A1B2C3D4-E5F6-7890-ABCD-000000000002</string>
				<key>UUID</key>
				<string>A1B2C3D4-E5F6-7890-ABCD-${uuid_suffix}</string>
				<key>UnlockPlugin</key>
				<false/>
				<key>UnlocalizedApplications</key>
				<array>
					<string>Automator</string>
				</array>
				<key>arguments</key>
				<dict/>
				<key>isViewVisible</key>
				<integer>1</integer>
				<key>location</key>
				<string>309.000000:253.000000</string>
				<key>nibPath</key>
				<string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
			</dict>
			<key>isViewVisible</key>
			<integer>1</integer>
		</dict>
	</array>
	<key>connectors</key>
	<dict/>
	<key>workflowMetaData</key>
	<dict>
		<key>serviceApplicationBundleID</key>
		<string>com.apple.finder</string>
		<key>serviceApplicationPath</key>
		<string>/System/Library/CoreServices/Finder.app</string>
		<key>serviceInputTypeIdentifier</key>
		<string>com.apple.Automator.fileSystemObject</string>
		<key>serviceOutputTypeIdentifier</key>
		<string>com.apple.Automator.nothing</string>
		<key>serviceProcessesInput</key>
		<integer>0</integer>
		<key>workflowTypeIdentifier</key>
		<string>com.apple.Automator.servicesMenu</string>
	</dict>
</dict>
</plist>
EOF

  echo "Installed: ${workflow_dir}"
}

# Enable service in Finder context menu + Services menu (Automator key format).
# Keys in pbs NSServicesStatus include literal double quotes around the name.
enable_service() {
  local display_name="$1"
  local key="\"(null) - ${display_name} - runWorkflowAsService\""
  defaults write pbs NSServicesStatus -dict-add "${key}" \
    '{ enabled_context_menu = 1; enabled_services_menu = 1; }'
}

main() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "error: macOS only" >&2
    exit 1
  fi
  if [[ ! -f "$SRC_RUNNER" ]]; then
    echo "error: missing $SRC_RUNNER" >&2
    exit 1
  fi

  local cli
  cli="$(resolve_cli)"

  mkdir -p "$CONF_DIR" "$SERVICES_DIR"
  cp "$SRC_RUNNER" "$RUNNER_DST"
  chmod +x "$RUNNER_DST"

  cat > "$CONF_FILE" <<EOF
# Generated by desktop/macos/install.sh — re-run install after upgrading CLI.
# PRESET empty = same as bare CLI (black headings). Set e.g. PRESET="technical" for blue.
CLI="${cli}"
PRESET=""
EXTRA_ARGS=""
EOF

  # Only Markdown / DOCX UTIs — do not include public.item/data (matches everything).
  local md_types
  md_types="$(cat <<'TYPES'
				<string>net.daringfireball.markdown</string>
				<string>net.ia.markdown</string>
				<string>org.vim.markdown-file</string>
				<string>com.unknown.md</string>
				<string>public.markdown</string>
TYPES
)"

  local docx_types
  docx_types="$(cat <<'TYPES'
				<string>org.openxmlformats.wordprocessingml.document</string>
				<string>com.microsoft.word.openxml.document</string>
TYPES
)"
  write_workflow "$CONVERT_NAME" "convert" "$md_types" "0000000000C1"
  write_workflow "$REVERSE_NAME" "reverse" "$docx_types" "0000000000R1"

  enable_service "$CONVERT_NAME"
  enable_service "$REVERSE_NAME"

  # Refresh Services menu
  /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
    -f "$SERVICES_DIR/${CONVERT_NAME}.workflow" 2>/dev/null || true
  /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
    -f "$SERVICES_DIR/${REVERSE_NAME}.workflow" 2>/dev/null || true
  /System/Library/CoreServices/pbs -flush 2>/dev/null || true
  /System/Library/CoreServices/pbs -update 2>/dev/null || true
  killall Finder 2>/dev/null || true

  echo
  echo "Done. CLI: ${cli}"
  echo "Config: ${CONF_FILE}"
  echo
  echo "In Finder (bottom of menu / Services):"
  echo "  • .md / .markdown → ${CONVERT_NAME}"
  echo "  • .docx → ${REVERSE_NAME}"
  echo "  (folders and other types do not show these items)"
  echo
  echo "If menus are missing:"
  echo "  System Settings → General → Login Items & Extensions → Extensions → Finder"
  echo "  (or Keyboard → Keyboard Shortcuts → Services), then re-run install / log out."
  echo "Uninstall: bash desktop/macos/uninstall.sh"
}

main "$@"
