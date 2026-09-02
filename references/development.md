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
- `test_docx_output.py` — XML assertions on generated .docx (code styles, table borders, fonts, H5/H6)

Requirements: `pytest`, `python-docx`, `lxml`, and `pandoc` must be available.

## Rebuild the Word reference template

When changing fonts, heading sizes, or table borders:

```bash
pip install python-docx   # if not already installed via [dev]
md-to-docx build reference
# or:
python3 -m md_to_docx.reference
```

Rebuild preset and native templates:

```bash
md-to-docx build presets
# or:
python3 -m md_to_docx.presets_build
```

Regenerates `assets/reference-wecom.docx`. A temporary `assets/reference-default.docx` may be created (gitignored). Requires `pandoc` on PATH.

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
.md → content normalize → layout spacing → mermaid → PNG (optional) → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

Content normalization fixes tables (separator row, column count), list spacing, heading levels, unclosed code blocks, inline formatting, and similar issues before pandoc runs.

## Contributing

1. Edit code under `scripts/md_to_docx/`
2. Add or update tests in `tests/`
3. Run `pytest tests/ -v`
4. Update `CHANGELOG.md` for user-visible changes
