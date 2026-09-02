# Roadmap

md-to-docx is evolving from a pandoc-based CLI into a full document compiler. The current release (v0.1) focuses on reliable Markdown → DOCX conversion with CJK support.

## Planned phases

| Phase | Focus | Status |
|-------|-------|--------|
| **P0** | Productization — README, examples, GitHub hygiene | Current |
| **P1A** | Native Document AST | Planned (v0.2) |
| **P1B** | Template presets (`--preset`) | Planned |
| **P1C** | Mermaid, math, captions | Planned |
| **P2+** | Web playground, plugins, MCP | Future |

## Full plan index

See [`aim/00-INDEX.md`](../aim/00-INDEX.md) for the complete roadmap with dependencies and scope.

**Note:** There is no online playground or web UI yet. Use `./bin/convert` or `python -m md_to_docx` for all conversions.
