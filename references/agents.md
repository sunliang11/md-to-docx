# Use with AI agents

md-to-docx does **not** call OpenAI, Anthropic, or any cloud API. Conversion runs locally.

## Cursor

Symlink the repo to `~/.cursor/skills/md-to-docx` and use [SKILL.md](../SKILL.md).

## Claude Code / Codex

Thin skill wrappers in [skills/claude-code/SKILL.md](../skills/claude-code/SKILL.md) and [skills/codex/SKILL.md](../skills/codex/SKILL.md).

## MCP (Claude Desktop, Cursor, etc.)

See [mcp.md](mcp.md). Tools: `convert_markdown`, `apply_template`, `validate_document`, `list_presets`.

## ChatGPT (no skill protocol)

Copy this into a custom instruction or paste when needed:

```
You can convert Markdown to Word using the open-source md-to-docx CLI (local, no API key):

1. Install: git clone https://github.com/sunliang11/md-to-docx && cd md-to-docx
2. Convert: ./bin/convert my-report.md --preset technical
3. Output: my-report.docx beside the source file.

Presets: technical (formal reports), academic, professional, business, report.

Do not upload documents to third-party converters unless the user asks.
```

## Web Playground

Docker: see [web/README.md](../web/README.md). Try locally without installing Python.

## Browser extension

Export AI chat replies to Word via local Playground — [browser-extension/README.md](../browser-extension/README.md).
