---
name: md-to-docx
description: Convert Markdown to professional Word DOCX via md-to-docx CLI.
---

# md-to-docx (Claude Code)

Symlink or clone [md-to-docx](https://github.com/sunliang11/md-to-docx), then:

```bash
/path/to/md-to-docx/bin/convert your-report.md --preset technical
```

Presets: `technical` (reports), `academic`, `professional`, `business`, `report`, `wecom` (企微).

No pip required — `bin/convert` sets `PYTHONPATH` automatically.

MCP: `pip install -e /path/to/md-to-docx[mcp]` then `md-to-docx-mcp`. See `references/mcp.md`.
