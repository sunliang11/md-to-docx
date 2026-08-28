# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-28

### Added

- Initial open-source release migrated from Cursor skill `md_to_docx`
- `md-to-docx` CLI for batch Markdown → DOCX conversion (pandoc + optional mermaid-cli)
- `md-to-docx-build-reference` CLI to rebuild WeCom-style reference template
- WeCom layout Lua filter and bundled `reference-wecom.docx`
- Markdown spacing normalization for cleaner DOCX output
- Mermaid block pre-rendering to PNG beside source files
