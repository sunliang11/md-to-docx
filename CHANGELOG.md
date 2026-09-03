# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Web Playground modes: Convert (validate, ODM inserts, community templates, engine HTML preview), Reverse, and Diff

### Changed

- `md-to-docx reverse INPUT` writes `INPUT` with a `.md` suffix in the same directory when `-o` is omitted

## [1.1.0] - 2026-09-03

### Removed

- `--preset wecom` and the pandoc conversion engine (`--engine pandoc`, `MD_TO_DOCX_ENGINE`)
- Bundled `reference-wecom.docx` / `wecom-layout.lua` and `md-to-docx build reference`
- WeCom import guide (`references/wecom-import.md`)
- Pandoc reverse fallback (`md-to-docx reverse --engine pandoc`)
- Separate console script `md-to-docx-mcp` — use `md-to-docx mcp` instead
- Vestigial `engine` parameters on convert/reverse APIs and preset objects

### Fixed

- Codespaces Web Playground startup — wait for `/healthz`, clearer failure logs, `waitFor: postStartCommand`

### Changed

- **Native-only compiler** — Markdown → Document AST → python-docx; no external document converter
- **CLI consolidation** — PATH only installs `md-to-docx`; use `md-to-docx build presets|all` and `md-to-docx mcp`
- Mermaid/captions transforms live in built-in plugins; `MD_TO_DOCX_MERMAID_WIDTH` is honored by `mmdc`
- GitHub Action docs pin to `@v1.1.0` (floating major: `@v1`)
- `editorial` preset available on CLI and bundled in the wheel

### Added (P3A / P3B / P4 Gate A / P2)

- **DOCX reverse** — `md-to-docx reverse in.docx -o out.md`
- **AST diff** — `md-to-docx diff a b [--format text|json|md]`
- **GitHub Action** — `action/action.yml` composite action for CI DOCX builds
- **Plugin API** — `--plugin PATH`, `--no-plugins`; built-in mermaid/math/captions
- **VS Code / Obsidian** editor integrations under `editors/`
- **Python API** (`md_to_docx.api.convert`), **MCP server**, **Web Playground**, **browser extension**
- **Open Document Markdown spec** — `spec/document-markdown.md` (`odm-0.1`)
- **Callouts** — `:::warning`, `:::info`, `:::note` containers
- **Community templates** — `templates/` with contribution guide
- Experimental HTML renderer (`md_to_docx.render.html.render_html`)

## [1.0.0] - 2026-09-02

### Added

- **Native Document AST engine** (default) — Parser → AST → python-docx renderer
- Dual-engine era flags (removed in 1.1.0): `--engine {native,pandoc}`, `--preset wecom`
- `--template`, `--toc`, `--title`, `--author`, `--date`, `--numbering`, header/footer page numbers
- Template presets: `--preset professional|technical|academic|business|report`
- `--check` document validation (`--check --format json`, `--strict`)
- Mermaid rendering in native engine (PNG embed; SVG saved to `{stem}-media/`)
- Math formulas via OMML (basic LaTeX via `latex2mathml`)
- Figure/table captions, cross-references (`{#fig:id}`, `[@fig:id]`), footnotes
- Built-in templates: `assets/reference-native.docx`, `assets/presets/*.docx`

### Changed

- Default engine became **native** (earlier builds were pandoc-oriented)
- Package name `md2docx-compiler` on PyPI; CLI command remains `md-to-docx`
