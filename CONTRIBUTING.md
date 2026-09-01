# Contributing

Thanks for helping improve md-to-docx.

## Project layout

This repo is a **Cursor Agent Skill** first. Python packaging is optional.

```
md-to-docx/
├── SKILL.md              # Agent entry point
├── bin/convert           # No-pip wrapper (sets PYTHONPATH)
├── scripts/md_to_docx/   # Python package
├── assets/               # Bundled pandoc assets
├── references/           # Detailed docs
└── tests/
```

## Setup

Requires **Python 3.10+** and **pandoc** on PATH.

**Skill checkout (no pip):**

```bash
./bin/convert --help
pytest tests/ -v   # may need: pip install -e ".[dev]"
```

**Editable install:**

```bash
pip install -e ".[dev]"
python -m md_to_docx --help
```

## Making changes

1. Edit code under `scripts/md_to_docx/`
2. Add or update tests in `tests/`
3. Run `pytest tests/ -v`
4. Update `CHANGELOG.md` for user-visible changes

## Tests

```bash
pytest tests/ -v
```

Integration tests require `pandoc`. DOCX XML assertions also need `lxml` (included in `[dev]`).

## Rebuild reference template

When changing Word styles:

```bash
python3 -m md_to_docx.reference
```

Regenerates `assets/reference-wecom.docx`.
