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

### Added (P0)
