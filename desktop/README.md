# Desktop context menu — Finder / Explorer

One-click install of **system right-click** actions for **md-to-docx** (current user only — no admin).

| File | Action |
|------|--------|
| `.md` / `.markdown` | **Convert to Word (md-to-docx)** → `md-to-docx <file> --preset technical` |
| `.docx` | **Reverse to Markdown (md-to-docx)** → `md-to-docx reverse <file>` |

Output is written beside the source file (same as the CLI).

## Prerequisites

1. Install the CLI so it is on your `PATH` (or set `MD_TO_DOCX_CLI` to an absolute path):

```bash
pip install -e .          # from a clone of this repo
which md-to-docx          # macOS / Linux
where md-to-docx          # Windows
```

2. Run the platform installer below from the **repo root**.

## Install

### macOS (Finder Services)

```bash
bash desktop/macos/install.sh
```

Then in Finder: right-click a `.md` or `.docx` and look near the **bottom** of the menu for **Convert to Word (md-to-docx)** / **Reverse to Markdown (md-to-docx)**. With few Services enabled they appear inline; with many they sit under **Services**.

If the items are missing:

1. **System Settings → General → Login Items & Extensions → Extensions → Finder** (enable the md-to-docx entries), or
2. **System Settings → Keyboard → Keyboard Shortcuts → Services**, or
3. Re-run `install.sh`, or log out and back in.

### Windows (Explorer)

```powershell
powershell -ExecutionPolicy Bypass -File desktop/windows/install.ps1
```

Then in Explorer: right-click a `.md` or `.docx` file.

## Uninstall

```bash
# macOS
bash desktop/macos/uninstall.sh
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File desktop/windows/uninstall.ps1
```

Uninstall removes only the context-menu hooks and local runner/config. It does **not** uninstall the `md-to-docx` Python package.

## Configuration

| Platform | Config file |
|----------|-------------|
| macOS | `~/Library/Application Support/md-to-docx/context-menu.conf` |
| Windows | `%LOCALAPPDATA%\md-to-docx\context-menu.conf` |

```bash
CLI="/absolute/path/to/md-to-docx"
PRESET="technical"
EXTRA_ARGS=""
```

- **CLI** — absolute path baked in at install time (GUI launchers often lack your shell `PATH`).
  On macOS the installer resolves **Homebrew or root pyenv** to `~/.pyenv/versions/<ver>/bin/md-to-docx` (never write a `shims/` path into the config — Finder cannot run shims).
- **PRESET** — passed as `--preset` for convert (default `technical`).
- **EXTRA_ARGS** — optional extra CLI flags (space-separated).
- **`MD_TO_DOCX_CLI`** — if set at install or run time, overrides the config `CLI`.

After upgrading the CLI, re-run the install script so the absolute path stays correct.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Menu missing (macOS) | Look at the **bottom** of the Finder context menu / **Services**; enable under General → Login Items & Extensions → Extensions → Finder (or Keyboard Shortcuts → Services); re-run install / log out |
| Menu click does nothing (macOS) | Re-run `bash desktop/macos/install.sh`; check `~/Library/Logs/md-to-docx/context-menu.log` — if there is no `START` line after clicking, the Service did not run (not a CLI failure) |
| Menu missing (Windows) | Re-run `install.ps1`; check HKCU `SystemFileAssociations` keys were created |
| “CLI not found” notification | Put `md-to-docx` on PATH, set `MD_TO_DOCX_CLI`, re-run install |
| Convert works in terminal but not from menu | Installer must bake an absolute path — re-run install from a shell where `which`/`where` works |
| Wrong preset | Edit `PRESET=` in the config file (no reinstall needed) |

## Layout

```
desktop/
  README.md / README.zh.md
  macos/install.sh  uninstall.sh  lib/runner.sh
  windows/install.ps1  uninstall.ps1  lib/runner.ps1
```
