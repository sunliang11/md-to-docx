# Development

## Setup

Requires **Python 3.10+**.

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e ".[dev]"
```

## Run tests

```bash
pytest tests/ -v
```

Test suite includes:
- `test_normalize.py` — Markdown normalization functions
- `test_unit.py` — Unit tests for mermaid regex, file collection, env parsing
- `test_cli.py` — CLI flags (--version, --help, sample conversion)
- `test_native_docx.py` — Native DOCX output assertions

Requirements: `pytest`, `python-docx`, and `lxml` must be available.

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

Optional Mermaid blocks are rendered to PNG via `mmdc` when available (native media under `{stem}-media/`).

## Contributing

1. Edit code under `scripts/md_to_docx/`
2. Add or update tests in `tests/`
3. Run `pytest tests/ -v`
4. Update `CHANGELOG.md` for user-visible changes
