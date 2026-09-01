# Configuration

## CLI Options

The converter supports command-line options for batch processing:

```bash
python3 -m md_to_docx <path> [options]
```

| Option | Default | Purpose |
|--------|---------|---------|
| `--version` | N/A | Display version and exit |
| `--exclude PATTERN` | _(see below)_ | Exclude files matching pattern (can be used multiple times) |
| `--output-dir DIR` | _(beside source)_ | Write .docx files to a specific directory |
| `--skip-existing` | False | Skip conversion if output .docx already exists |
| `--dry-run` | False | Print files that would be converted without converting them |

**Default exclusions:** `README.md`, `CHANGELOG.md`, `SKILL.md`, `.github/**` plus `.git/` and `node_modules/` (always excluded).

Example:

```bash
python3 -m md_to_docx ./docs --exclude "*.draft.md" --output-dir ./output
```

## Environment Variables

Environment variables control Mermaid rendering. All are optional.

| Variable | Default | Purpose |
|----------|---------|---------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | PNG render scale for Mermaid diagrams (higher = sharper, larger files) |
| `MD_TO_DOCX_MERMAID_WIDTH` | _(unset)_ | Optional `mmdc -w` width in pixels (e.g. `1200`) |
| `MD_TO_DOCX_BROWSER` | auto-detect | Browser executable path for `mmdc` |
| `PUPPETEER_EXECUTABLE_PATH` | auto-detect | Same as above (Puppeteer / mmdc convention) |

## Examples

Higher-resolution Mermaid output:

```bash
MD_TO_DOCX_MERMAID_SCALE=5 python3 -m md_to_docx ./docs
```

Fixed width plus scale:

```bash
MD_TO_DOCX_MERMAID_SCALE=5 MD_TO_DOCX_MERMAID_WIDTH=1400 python3 -m md_to_docx ./docs
```

Custom browser on Linux:

```bash
MD_TO_DOCX_BROWSER=/usr/bin/google-chrome python3 -m md_to_docx report.md
```

## Auto-detected browser paths

The converter checks these locations (in order) when `MD_TO_DOCX_BROWSER` is unset:

- macOS: Google Chrome, Microsoft Edge, Chromium under `/Applications/`
- Linux: `/usr/bin/google-chrome`, `/usr/bin/chromium-browser`, `/usr/bin/chromium`

## Bundled assets

Conversion uses files in `assets/` (or the packaged copies under `md_to_docx/data/`):

- `reference-wecom.docx` — Word styles for WeCom-like output
- `wecom-layout.lua` — Pandoc Lua filter (code blocks, wide tables, image width)
