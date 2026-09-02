# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-09-02

### Added

- **Native Document AST engine** (default) — Parser → AST → python-docx renderer; no pandoc required
- `--engine {native,pandoc}` with `MD_TO_DOCX_ENGINE` env override
- `--template`, `--toc`, `--title`, `--author`, `--date`, `--numbering`, header/footer page numbers
- Template presets: `--preset professional|technical|academic|business|report|wecom`
- `--check` document validation (`--check --format json`, `--strict`)
- Mermaid rendering in native engine (PNG embed; SVG saved to `{stem}-media/`)
- Math formulas via OMML (basic LaTeX via `latex2mathml`)
- Figure/table captions, cross-references (`{#fig:id}`, `[@fig:id]`), footnotes
- Built-in templates: `assets/reference-native.docx`, `assets/presets/*.docx`
- CI `test-native` job (no pandoc)

### Changed

- Default engine is **native** (was pandoc-only in v0.1)
- Package name `md2docx-compiler` on PyPI; CLI command remains `md-to-docx`
- WeCom import: use `--preset wecom` or `--engine pandoc` (unchanged Lua pipeline)

## [Unreleased]

### Added (P4 Gate A)

- **Open Document Markdown spec** — `spec/document-markdown.md` (`odm-0.1`)
- **Callouts** — `:::warning`, `:::info`, `:::note` containers with colored left border in DOCX
- **Community templates** — `templates/` directory with four official examples and contribution guide
- **Experimental HTML renderer** — `md_to_docx.render.html.render_html()` for AST preview (not CLI-exposed)
- CI validates `templates/**/sample.md` conversion

## [1.1.0] - 2026-09-02

### Added (P3A)

- **DOCX reverse** — `md-to-docx reverse in.docx -o out.md` (native AST parser; `--engine pandoc` fallback)
- **AST diff** — `md-to-docx diff a b [--format text|json|md]`
- **GitHub Action** — `action/action.yml` composite action for CI DOCX builds
- `references/roundtrip.md` — support matrix and limitations
- `lxml` promoted to runtime dependency

### Added (P3B)

- **Plugin API** — `--plugin PATH`, `--no-plugins`; built-in mermaid/math/captions plugins
- **VS Code extension** — `editors/vscode/` (`MD: Export to DOCX`)
- **Obsidian plugin** — `editors/obsidian/` (desktop CLI spawn)
- `examples/plugins/uppercase_headings.py` — third-party plugin sample
- `references/plugins.md`

### Changed

- Mermaid/captions transforms migrated to plugin hooks (behavior compatible with P1C)

## [Unreleased — P2 archive]

### Added (P2)

- **Python API** (`md_to_docx.api.convert`) for Skill, MCP, and Web
- **MCP server** (`md-to-docx-mcp`) — `convert_markdown`, `apply_template`, `validate_document`, `list_presets`
- **Skill matrix** — Claude Code, Codex, Gemini CLI wrappers under `skills/`
- **Web Playground** — FastAPI + Docker (`web/`)
- **Browser extension** — Export AI chat to Word (`browser-extension/`)

### Added (P0)
