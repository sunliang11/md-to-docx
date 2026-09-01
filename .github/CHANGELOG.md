# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `bin/convert` — run converter without `pip install -e` (sets `PYTHONPATH` for Cursor skill checkouts)
- Auto-build `reference-wecom.docx` on first run when missing (requires `python-docx`)
- Bilingual `README.md` for GitHub visitors (English + 中文)
- Agent troubleshooting table in `SKILL.md` (`No module named md_to_docx`, hatchling timeout)

### Changed

- `SKILL.md` / `references/installation.md`: skill-first workflow; pip install is optional fallback
- `SKILL.md` remains the Agent entry point; `README.md` is for human visitors
- Move changelog to `.github/CHANGELOG.md`
- SKILL.md frontmatter: only `name` and `description` (env requirements in description)
- Remove duplicate assets under `src/md_to_docx/data/`

### Previously (0.1.0 restructuring)

- Restructured as a standard Agent Skill: `assets/`, `references/`, concise `SKILL.md`
- Skill `name` renamed to `md-to-docx` (was `md_to_docx`); symlink folder should match
- Primary entry point is `python -m md_to_docx` (console scripts kept for compatibility)
- Bundled assets moved from `src/md_to_docx/data/` to `assets/`
- Removed redundant `cli.py` module

## [0.1.0] - 2026-08-28

### Added

- Initial open-source release migrated from Cursor skill `md_to_docx`
- `md-to-docx` CLI for batch Markdown → DOCX conversion (pandoc + optional mermaid-cli)
- `md-to-docx-build-reference` CLI to rebuild WeCom-style reference template
- WeCom layout Lua filter and bundled `reference-wecom.docx`
- Markdown spacing normalization for cleaner DOCX output
- Mermaid block pre-rendering to PNG beside source files
