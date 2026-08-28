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

## Rebuild the Word reference template

When changing fonts, heading sizes, or table borders:

```bash
pip install python-docx   # if not already installed via [dev]
python3 -m md_to_docx.reference
# or (legacy alias):
md-to-docx-build-reference
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
.md → normalize spacing → mermaid → PNG (optional) → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

## Contributing

1. Edit code under `scripts/md_to_docx/`
2. Add or update tests in `tests/`
3. Run `pytest tests/ -v`
4. Update `.github/CHANGELOG.md` for user-visible changes
