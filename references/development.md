# Development

## Setup

Requires **Python 3.10+**.

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e ".[dev,mcp,web]"
```

## Run tests

```bash
pytest tests/ -v
```

`lxml` is a runtime dependency. Mermaid rendering needs `mmdc` on PATH; CI does not install it (diagrams are optional unless `--strict-mermaid`).

## Python API

```python
from pathlib import Path
from md_to_docx.api import convert, validate_markdown

result = convert(
    source=Path("report.md"),
    output=Path("report.docx"),
    preset="technical",
)
print(result.output_path, result.warnings)

# Or from text:
result = convert(markdown_text="# Hello\n\nWorld.", preset="professional")

issues = validate_markdown("# Title\n\n")
```

`convert()` accepts a file path or `markdown_text=`, optional `preset` / `template`, TOC and metadata flags. See `scripts/md_to_docx/api.py`.

## Rebuild templates

When changing fonts, heading sizes, or table borders:

```bash
md-to-docx build presets
# or:
python3 -m md_to_docx.presets_build
```

Regenerates `assets/presets/*.docx` and `assets/reference-native.docx`.

## Project layout

```
md-to-docx/
├── SKILL.md
├── scripts/md_to_docx/   # Python package
├── assets/               # Bundled conversion assets
├── references/           # Detailed docs (loaded on demand)
└── tests/
```

## Conversion pipeline

```
.md → content normalize → layout spacing → Document AST → native DOCX renderer → .docx
```

Content normalization fixes tables (separator row, column count), list spacing, heading levels, unclosed code blocks, inline formatting, and similar issues before parsing.

Optional Mermaid blocks are rendered to PNG via `mmdc` when available (native media under `{stem}-media/`). Scale/width: `MD_TO_DOCX_MERMAID_SCALE`, `MD_TO_DOCX_MERMAID_WIDTH`.

## Contributing

1. Edit code under `scripts/md_to_docx/`
2. Add or update tests in `tests/`
3. Run `pytest tests/ -v`
4. Update `CHANGELOG.md` for user-visible changes
