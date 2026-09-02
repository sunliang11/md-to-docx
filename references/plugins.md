# Plugin API

md-to-docx exposes a minimal **Plugin** protocol for AST transforms. Plugins are explicit Python files loaded via `--plugin` (no marketplace in v1.1).

## Protocol

```python
from pathlib import Path
from dataclasses import dataclass
from md_to_docx.plugin.base import PluginBase, PluginContext
from md_to_docx.ast import nodes as n

class MyPlugin(PluginBase):
    name = "my_plugin"

    def render_assets(self, document: n.Document, ctx: PluginContext) -> tuple[n.Document, dict[str, Path]]:
        # Optional: render side-effect assets (e.g. Mermaid → PNG)
        return document, {}

    def transform(self, document: n.Document, ctx: PluginContext) -> n.Document:
        # Modify AST before DOCX render
        return document

plugin = MyPlugin()
```

Two hooks only:

| Hook | Purpose |
|------|---------|
| `render_assets` | Side effects + asset paths (Mermaid PNG) |
| `transform` | Pure AST mutation |

## CLI

```bash
# Built-in plugins (mermaid, math, captions) — default on
md-to-docx report.md

# Disable built-ins (debugging)
md-to-docx report.md --no-plugins

# Load custom plugin
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py
```

## Built-in plugins

| Plugin | Hook | Role |
|--------|------|------|
| `mermaid` | `render_assets` | `mmdc` → PNG in `{stem}-media/` |
| `math` | — | Placeholder (math at parse/render) |
| `captions` | `transform` | Figure/table numbering |

## Example

See [`examples/plugins/uppercase_headings.py`](../examples/plugins/uppercase_headings.py).

## Warnings

- **Do not** `import python-docx` in plugins — operate on AST only
- Plugins run **after** parse, **before** DOCX render
- `reverse` does not load plugins (DOCX → MD path is parse-only)
- No `setuptools` entry points yet (planned for P4)
