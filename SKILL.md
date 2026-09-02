---
name: md-to-docx
description: >-
  Converts AI-generated Markdown to professional Word DOCX. Use --preset technical
  for formal reports; --preset wecom for 企微导入. Native engine by default (no pandoc).
---

# md-to-docx

Turn **AI-generated Markdown** into **professional Word documents**. Default engine is **native** (Document AST). MCP and Web Playground available for agent workflows.

## Quick start (Cursor skill — **no pip install**)

Skill root = directory containing this `SKILL.md` (e.g. `~/.cursor/skills/md-to-docx`).

```bash
# Formal technical report
"<skill-root>/bin/convert" report.md --preset technical --toc --numbering

# General document
"<skill-root>/bin/convert" report.md --preset professional

# WeCom smart-doc import (pandoc)
"<skill-root>/bin/convert" report.md --preset wecom

# Fallback
PYTHONPATH="<skill-root>/scripts" python3 -m md_to_docx report.md --preset technical
```

**Do not** run `pip install` first when using a local skill checkout — use `bin/convert` or `PYTHONPATH`.

## Agent workflow

1. Resolve **skill-root** (parent of `bin/convert`).
2. Choose preset by user intent:
   - 企微 / WeCom import → `--preset wecom`
   - Formal technical / design doc → `--preset technical --toc --numbering`
   - Academic paper → `--preset academic`
   - Business summary → `--preset business`
3. Run conversion; **do not edit** source `.md`.
4. Report output `.docx` path to the user.
5. If markdown contains ` ```mermaid ` blocks, ensure `mmdc` is on PATH or warn user.
6. For MCP clients: see [references/mcp.md](references/mcp.md) (`pip install .[mcp]`, `md-to-docx-mcp`).
7. **Reverse** (user gives DOCX, wants Markdown source): `md-to-docx reverse file.docx -o file.md` — see [references/roundtrip.md](references/roundtrip.md).
8. **Diff** two report versions: `md-to-docx diff v1.md v2.md --format md`.

Do not automate WeCom upload.

## Behavior

- Original `.md` files are never modified
- Output `.docx` beside source (`foo.md` → `foo.docx`) unless `--output-dir`
- Mermaid → PNG in `{stem}mermaid图片/` or native `{stem}-media/`
- Per-file failures reported; exit non-zero if any failed

## Troubleshooting

| Error | Fix |
|-------|-----|
| `No module named md_to_docx` | Use `bin/convert` or `PYTHONPATH=<skill-root>/scripts` |
| `` `pandoc` not found `` | Only for `--preset wecom`; or `brew install pandoc` |
| `` `mmdc` not found `` | `npm i -g @mermaid-js/mermaid-cli` or remove mermaid blocks |
| Template missing | `PYTHONPATH=scripts python -m md_to_docx.presets_build` |

## Resources

- [Roundtrip / reverse / diff](references/roundtrip.md)
- [Plugin API](references/plugins.md)
- [MCP setup](references/mcp.md)
- [Use with ChatGPT](references/agents.md)
- [Presets](references/presets.md)
- [Web Playground](web/README.md)
- [WeCom import](references/wecom-import.md)
