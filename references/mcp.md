# MCP server

Local MCP server for Markdown → DOCX. No API keys.

Start with the main CLI:

```bash
md-to-docx mcp
```

## Install

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e ".[mcp]"
```

## Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "md-to-docx": {
      "command": "md-to-docx",
      "args": ["mcp"]
    }
  }
}
```

Or with full path / module entry:

```json
{
  "mcpServers": {
    "md-to-docx": {
      "command": "/path/to/python",
      "args": ["-m", "md_to_docx.mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `convert_markdown` | `input_path` or `markdown` → local `output_path` (.docx) |
| `apply_template` | `input_path` + `template` + `output_path` |
| `validate_document` | Check markdown without converting |
| `list_presets` | List preset names and descriptions |

`render_preview` is **not** in MCP v2.0 — use the [Web Playground](../web/README.md) for HTML preview.

## Output path safety

`output_path` must be under:

- Current working directory
- Parent directory of `input_path`
- `MD_TO_DOCX_OUT` (if set)

## Errors

Failures return JSON with `problem`, `cause`, `fix`, and `docs` URL.

## Verify

```bash
md-to-docx mcp --help
md-to-docx mcp --version
# or: python -m md_to_docx.mcp --version
```
