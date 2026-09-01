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

## Quick start (Cursor skill — **no pip install**)

Skill root = directory containing this `SKILL.md` file (may be `~/.cursor/skills/md_to_docx` or `md-to-docx`).

```bash
# Preferred: wrapper script (sets PYTHONPATH automatically)
"<skill-root>/bin/convert" <path>          # .md file or directory (recursive)

# Fallback: explicit PYTHONPATH
PYTHONPATH="<skill-root>/scripts" python3 -m md_to_docx <path>
```

**Do not** run `pip install` as the first step when using a local skill checkout — it often fails (hatchling timeout) and is unnecessary.

Only if both commands above fail with `No module named md_to_docx`, try:

```bash
pip install -e "<skill-root>"
```

System deps: **Python 3.10+**, **pandoc** on PATH. **mmdc** only when `.md` contains ` ```mermaid ` blocks.

## Agent workflow

1. Resolve **skill-root** (parent of `bin/convert`, or parent of `scripts/`).
2. Confirm **pandoc** on PATH: `which pandoc`
3. Run `"<skill-root>/bin/convert" <user's .md or directory>`
4. If `reference-wecom.docx` missing, converter auto-builds it (needs `python-docx`; else restore from repo `assets/`)
5. Summarize created `.docx` and any `*_mermaid_*.png` paths; **do not edit** source `.md`
6. Remind user to import manually — [references/wecom-import.md](references/wecom-import.md)

Do not automate WeCom upload.

## Behavior

- Original `.md` files are never modified
- Output `.docx` is written next to each source file (`foo.md` → `foo.docx`)
- Mermaid blocks become PNGs beside the source (`foo_mermaid_01.png`, …)
- Per-file failures are reported; remaining files still convert; exit code is non-zero if any failed

## Troubleshooting (agents)

| Error | Fix |
|-------|-----|
| `No module named md_to_docx` | Use `bin/convert` or `PYTHONPATH=<skill-root>/scripts` — see Quick start |
| `pip install` / hatchling timeout | Skip pip; use `bin/convert` instead |
| `` `pandoc` not found `` | `brew install pandoc` (macOS) or install from pandoc.org |
| `reference doc missing` + build failed | `pip install python-docx` then `PYTHONPATH=… python3 -m md_to_docx.reference` |
| `` `mmdc` not found `` | Only needed for mermaid; `npm i -g @mermaid-js/mermaid-cli` |

## Resources

- [Installation](references/installation.md) — pip install (optional), pandoc, mmdc
- [Configuration](references/configuration.md) — environment variables
- [WeCom import](references/wecom-import.md) — import steps and acceptance checklist
- [Development](references/development.md) — rebuild reference template, tests
