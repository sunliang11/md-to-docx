# Contributing

Thanks for helping improve md-to-docx.

## Project layout

```
md-to-docx/
├── SKILL.md              # Agent entry point
├── bin/convert           # No-pip wrapper (sets PYTHONPATH)
├── scripts/md_to_docx/   # Python package
├── assets/               # Bundled templates, branding, demo
├── examples/             # Curated conversion examples
├── action/               # GitHub Action
├── web/                  # FastAPI playground
├── editors/              # VS Code / Obsidian
├── browser-extension/    # Browser export extension
├── references/           # Detailed docs
└── tests/
```

## Scope

Contributions are welcome across the shipped product surface:

- CLI / native Document AST engine / presets
- Python API, MCP server, Web Playground
- GitHub Action, editor integrations, browser extension
- Docs, examples, community templates under `templates/`

Historical planning notes live under `aim/` (archived — not the active roadmap). See [references/roadmap.md](references/roadmap.md).

## Setup

Requires **Python 3.10+**.

**Skill checkout (no pip):**

```bash
./bin/convert --help
pytest tests/ -v   # may need: pip install -e ".[dev]"
```

**Editable install:**

```bash
pip install -e ".[dev,mcp,web]"
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

`lxml` is a runtime dependency (used for DOCX XML assertions).

Mermaid diagrams need `mmdc` on PATH. CI does **not** install Mermaid CLI; diagram rendering is optional unless you pass `--strict-mermaid`.

## Rebuild templates

When changing Word styles:

```bash
md-to-docx build presets
# or: PYTHONPATH=scripts python3 -m md_to_docx.presets_build
```

Regenerates `assets/presets/*.docx` and `assets/reference-native.docx`.
