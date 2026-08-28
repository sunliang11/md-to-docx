---
name: md_to_docx
description: >-
  Converts Markdown files to DOCX via pandoc for WeCom (企微) smart-doc import.
  Recursively processes directories, renders Mermaid blocks to PNG with mermaid-cli,
  applies WeCom-like reference styles and layout normalization, leaves original
  .md untouched, writes .docx and PNGs beside each source file.
  Use when the user asks to convert md to docx, batch Markdown for 企微导入,
  preprocess mermaid for pandoc, or migrate docs into WeCom smart documents.
---

# md_to_docx

Batch-convert Markdown → DOCX for WeCom「导入本地文档」. Prefer this over pasting MD: tables, nested lists, heading levels, and embedded images survive best.

> **Development note:** This skill directory is a symlink to the open-source repo at
> `/Users/sunliang/workspace/source/md-to-docx`. Edit the repo directly; do not copy files into `~/.cursor/skills`.

## Pipeline

```
.md → normalize spacing → mermaid → PNG (optional) → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

1. **Preprocess** — normalize blank lines around headings, tables, code blocks, horizontal rules, images
2. **Mermaid** — render ` ```mermaid ` blocks to PNG beside the source file
3. **Pandoc** — GFM input, WeCom-style reference doc, Lua layout filter, 150 DPI images, preserve code wrapping

## Prerequisites (install on the machine beforehand)

- **pandoc** — required always (3.x with Lua support recommended)
- **@mermaid-js/mermaid-cli** (`mmdc`) — required only when a file contains ` ```mermaid ` blocks
- **Chrome / Edge / Chromium** — used by `mmdc` to render diagrams (script auto-detects common install paths; override with `PUPPETEER_EXECUTABLE_PATH` or `MD_TO_DOCX_BROWSER`)
- **python-docx** — only needed to rebuild the reference template via `md-to-docx-build-reference`

```bash
# macOS example
brew install pandoc
npm install -g @mermaid-js/mermaid-cli
pip3 install python-docx   # optional, for rebuilding reference template
pip install -e /Users/sunliang/workspace/source/md-to-docx   # dev install for CLI
```

## How to run

```bash
md-to-docx <path>
# or
python3 -m md_to_docx <path>
```

- `<path>` is a `.md` file → convert that file only
- `<path>` is a directory → recursively convert all `*.md` under it

**Behavior**

1. Original `.md` files are never modified
2. Output `.docx` is written next to each source md (`foo.md` → `foo.docx`)
3. Mermaid blocks are rendered to PNGs in the same directory (`foo_mermaid_01.png`, …), then referenced in a temp copy before pandoc
4. Uses bundled `reference-wecom.docx` for WeCom-like heading/body/code/table styles
5. Uses bundled `wecom-layout.lua` for code-block styling, wide-table compaction, default image width
6. Per-file failures are reported; remaining files still convert; exit code is non-zero if any failed

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | Mermaid PNG render scale (higher = sharper, larger file) |
| `MD_TO_DOCX_MERMAID_WIDTH` | _(unset)_ | Optional mmdc `-w` width in pixels (e.g. `1200`) |
| `MD_TO_DOCX_BROWSER` | auto-detect | Browser executable for mmdc |
| `PUPPETEER_EXECUTABLE_PATH` | auto-detect | Same as above (mmdc/puppeteer convention) |

Example:

```bash
MD_TO_DOCX_MERMAID_SCALE=5 MD_TO_DOCX_MERMAID_WIDTH=1400 md-to-docx ./docs
```

## Rebuild reference template

If you need to tweak Word styles (fonts, heading sizes, table borders):

```bash
md-to-docx-build-reference
```

This regenerates `src/md_to_docx/data/reference-wecom.docx` from pandoc's default reference plus WeCom-like customizations.

## Agent instructions

When the user asks to convert md→docx (especially for 企微):

1. Confirm `pandoc` is on PATH (`which pandoc`)
2. Confirm bundled reference doc exists; if missing, run `md-to-docx-build-reference`
3. Run `md-to-docx` (or `python3 -m md_to_docx`) with the target path the user gave
4. Summarize created `.docx` / mermaid `.png` paths; do not edit source md
5. Remind: import each docx manually in WeCom PC → 智能文档 → ・・・ → **导入本地文档**

Do **not** automate WeCom upload (Playwright). Manual import is the supported path.

## WeCom acceptance checklist

After converting a sample document:

1. **Layout** — H2/H3/H4 hierarchy is visible; blockquotes, code blocks, and body text have consistent spacing
2. **Tables** — bordered with readable header row; wide tables (>6 columns) use smaller compact font
3. **Images** — Mermaid diagrams and local screenshots are sharp enough at normal zoom
4. **Source safety** — original `.md` unchanged

## Format notes (set expectations)

- Local images in md are embedded into docx at 150 DPI; WeCom re-uploads them on import
- Mermaid must be pre-rendered to images or pandoc emits raw code fences
- For local screenshots, source width ≥1200px gives best results; script does not resample
- Very wide tables may still look tight in WeCom (compact style mitigates but cannot fully fix)
- Inline `` `code` `` and some Word styles may flatten after WeCom import — structure (headings, lists, tables) is preserved best
