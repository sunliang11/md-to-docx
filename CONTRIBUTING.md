# Contributing

Thanks for helping improve md-to-docx.

## Project layout

This repo is a **Cursor Agent Skill** first. Python packaging is optional.

```
md-to-docx/
├── SKILL.md              # Agent entry point
├── bin/convert           # No-pip wrapper (sets PYTHONPATH)
├── scripts/md_to_docx/   # Python package
├── assets/               # Bundled templates, branding, demo
├── examples/             # Curated conversion examples
├── references/           # Detailed docs
└── tests/
```

## Scope (Phase 0)

Please do not open PRs for a web app, MCP server, browser extension, or marketplace.
The current milestone is: make Markdown → DOCX excellent and the GitHub page trustworthy.
See `aim/` for the roadmap.

## Setup

Requires **Python 3.10+**.

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

DOCX XML assertions need `lxml` (included in `[dev]`).

## Rebuild templates

When changing Word styles:

```bash
md-to-docx build presets
# or: PYTHONPATH=scripts python3 -m md_to_docx.presets_build
```

Regenerates `assets/presets/*.docx` and `assets/reference-native.docx`.
