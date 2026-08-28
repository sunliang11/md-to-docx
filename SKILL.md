---
name: md-to-docx
description: >-
  Converts Markdown to DOCX via pandoc for WeCom (企微) smart-doc import.
  Renders Mermaid blocks to PNG, applies WeCom-like styles and layout normalization,
  leaves original .md untouched, writes .docx and PNGs beside each source file.
  Requires Python 3.10+, pandoc 3.x, mmdc when Markdown contains mermaid blocks.
  Use when converting md to docx, batch Markdown for 企微导入, preprocess mermaid for pandoc,
  or migrating docs into WeCom smart documents.
---

# md-to-docx

Batch-convert Markdown to DOCX for WeCom「导入本地文档」.

## Quick start

```bash
python3 -m md_to_docx <path>    # .md file or directory (recursive)
```

Install prerequisites — see [references/installation.md](references/installation.md).

## Workflow

1. Confirm **Python 3.10+** and **pandoc** are on PATH (`python3 --version`, `which pandoc`)
2. Confirm `assets/reference-wecom.docx` and `assets/wecom-layout.lua` exist; if missing, run `python3 -m md_to_docx.reference`
3. Run `python3 -m md_to_docx <path>` with the user's target path
4. Summarize created `.docx` and mermaid `.png` paths; do not edit source `.md`
5. Remind the user to import manually — see [references/wecom-import.md](references/wecom-import.md)

Do not automate WeCom upload. Manual import is the supported path.

## Behavior

- Original `.md` files are never modified
- Output `.docx` is written next to each source file (`foo.md` → `foo.docx`)
- Mermaid blocks become PNGs beside the source (`foo_mermaid_01.png`, …)
- Per-file failures are reported; remaining files still convert; exit code is non-zero if any failed

## Resources

- [Installation](references/installation.md) — Python, pandoc, mmdc, pip, Cursor skill symlink
- [Configuration](references/configuration.md) — environment variables
- [WeCom import](references/wecom-import.md) — import steps and acceptance checklist
- [Development](references/development.md) — rebuild reference template, tests
