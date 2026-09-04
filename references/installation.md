# Installation

**md-to-docx** is an open-source document compiler for the AI era — it turns Markdown and AI-generated content into professional Word documents.

See [README.md](../README.md) for a project overview.

## Two ways to use

| Mode | When | Command |
|------|------|---------|
| **Cursor skill (recommended)** | Repo/symlink under `~/.cursor/skills/` | `<skill-root>/bin/convert <path>` — **no pip install** |
| **Editable install** | CLI on PATH everywhere | `pip install -e .` then `python3 -m md_to_docx <path>` |

Agents and skill users should prefer **`bin/convert`** to avoid `No module named md_to_docx` and flaky `pip install -e` (hatchling / network timeouts).

## Requirements

| Component | Version | Required when |
|-----------|---------|---------------|
| **Python** | **3.10+** | Always (see `requires-python` in `pyproject.toml`) |
| **@mermaid-js/mermaid-cli** (`mmdc`) | Latest stable | Markdown files contain ` ```mermaid ` blocks |
| **Chrome / Edge / Chromium** | Any recent version | Mermaid rendering (`mmdc` uses a browser) |
| **python-docx** | 1.0+ | Always (runtime dependency) |

## Cursor skill (no pip)

Skill root = directory containing `SKILL.md` (folder may be `md-to-docx` or `md_to_docx`).

```bash
SKILL_ROOT=/path/to/md-to-docx   # or ~/.cursor/skills/md_to_docx

# Preferred
"$SKILL_ROOT/bin/convert" report.md
"$SKILL_ROOT/bin/convert" ./docs

# Equivalent
PYTHONPATH="$SKILL_ROOT/scripts" python3 -m md_to_docx report.md
```

Symlink example (folder name `md-to-docx` or `md_to_docx` both work):

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

Bundled assets live in `assets/` (`reference-native.docx`, `presets/*.docx`). Rebuild with `md-to-docx build presets` if missing.

## Install the Python package (optional)

For global `python3 -m md_to_docx` without setting `PYTHONPATH`:

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .
```

Or from GitHub (may hit hatchling / network errors on some mirrors):

```bash
pip install "git+https://github.com/sunliang11/md-to-docx.git"
```

> Not published on PyPI. The PyPI name `md-to-docx` is a different project.

## Install optional Mermaid tools

### macOS

```bash
npm install -g @mermaid-js/mermaid-cli   # only if you use mermaid in .md
```

### Linux

```bash
npm install -g @mermaid-js/mermaid-cli
```

Ensure a Chromium-based browser is installed, or set `MD_TO_DOCX_BROWSER` / `PUPPETEER_EXECUTABLE_PATH`.

## Verify installation

```bash
python3 --version          # must be 3.10+
./bin/convert --help       # from skill root, no pip
```

Convert a sample file:

```bash
./bin/convert tests/fixtures/sample.md --preset technical
```

## Desktop context menu

Install Finder / Explorer right-click actions (current user only). Requires `md-to-docx` on `PATH` first — see [Quick Start Option E](../README.md#quick-start) and [desktop/README.md](../desktop/README.md).

```bash
# macOS
bash desktop/macos/install.sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File desktop/windows/install.ps1
```

## Common errors

| Error | Fix |
|-------|-----|
| `No module named md_to_docx` | Use `./bin/convert` or `PYTHONPATH=<skill-root>/scripts python3 -m md_to_docx` |
| `pip install -e` / hatchling timeout | Skip pip; use `bin/convert` |
| `` `mmdc` not found `` | `npm install -g @mermaid-js/mermaid-cli` (only for mermaid blocks) |
| `mmdc failed` / browser errors | Install Chrome/Chromium or set `MD_TO_DOCX_BROWSER` |
| Template missing | `PYTHONPATH=scripts python -m md_to_docx.presets_build` |
| `Python 3.9` or older | Upgrade to Python 3.10+ |
| Context menu “CLI not found” | Re-run `desktop/*/install.*` from a shell where `md-to-docx` is on PATH, or set `MD_TO_DOCX_CLI` |
