English | [中文](README.zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml/badge.svg)](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

# md-to-docx

<img src="assets/branding/wordmark.svg" alt="md-to-docx: MD → DOCX" width="320">

**The open-source document compiler for the AI era.**

Turn Markdown and AI-generated content into professional Word documents.

[Documentation](references/installation.md) · [Examples](examples/README.md) · [GitHub](https://github.com/sunliang11/md-to-docx)

![Convert Markdown to DOCX](assets/demo/hero.gif)

**Before** (Markdown) → **After** (Word)

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">

## Quick Start

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md --preset technical
```

Try without installing Python (Docker Playground):

```bash
docker compose -f web/docker-compose.yml up --build
# open http://localhost:8080
```

**Pipeline:** Markdown / AI output → Document AST → Professional DOCX

**Status: v1.1 engine + v2 AI entry points + v3 roundtrip** — Native Document AST; MCP, Web Playground, browser extension; **reverse/diff**, GitHub Action, Plugin API, VS Code & Obsidian. WeCom import: `--preset wecom`.

## Features

- Native Document AST engine (default) — no pandoc required for most conversions
- Headings, lists, tables, code blocks, blockquotes, images, footnotes
- CJK-aware templates (Microsoft YaHei / SimSun)
- Mermaid diagrams → PNG (needs `mmdc`; native engine degrades to code block without it)
- Math formulas → OMML (basic LaTeX coverage)
- Figure/table captions and cross-references
- Template presets: `--preset technical|academic|business|professional|report`
- Word-native TOC (`--toc`), page numbers, header/footer
- `--check` document validation without converting
- Batch directory conversion
- Cursor Agent Skill
- WeCom smart-doc import (`--preset wecom` or `--engine pandoc`)
- MCP server (`md-to-docx-mcp`) — see [Use with AI](#use-with-ai)
- Web Playground (Docker) — browser editor + DOCX download
- Browser extension — Export AI chat replies to Word
- **DOCX reverse** — `md-to-docx reverse in.docx -o out.md` (native AST)
- **AST diff** — `md-to-docx diff a.md b.md [--format text|json|md]`
- **GitHub Action** — `uses: sunliang11/md-to-docx/action@v3` for CI DOCX builds
- **Plugin API** — `--plugin path/to/plugin.py`, `--no-plugins`
- **VS Code / Obsidian** — one-click export from your editor

## Use with AI

Turn AI-written Markdown into Word — **no API keys**, all local:

| Entry | Docs |
|-------|------|
| Cursor Skill | [SKILL.md](SKILL.md) |
| Claude Code / Codex | [skills/](skills/) |
| MCP | [references/mcp.md](references/mcp.md) — `pip install .[mcp]` |
| Web Playground | [web/README.md](web/README.md) — Docker |
| Browser extension | [browser-extension/README.md](browser-extension/README.md) |
| ChatGPT prompt | [references/agents.md](references/agents.md) |

## Editors

| Entry | Docs |
|-------|------|
| CLI | This README |
| VS Code | [editors/vscode/README.md](editors/vscode/README.md) |
| Obsidian | [editors/obsidian/README.md](editors/obsidian/README.md) |
| MCP | [references/mcp.md](references/mcp.md) |
| Browser | [browser-extension/README.md](browser-extension/README.md) |

## Git workflow

Keep **Markdown in Git**; treat **DOCX as a build artifact**:

```gitignore
dist/docx/
*.docx
```

Example CI job:

```yaml
- uses: sunliang11/md-to-docx/action@v3
  with:
    input: docs/report.md
    preset: technical
- uses: actions/upload-artifact@v4
  with:
    name: docx
    path: dist/docx
```

See [action/README.md](action/README.md) and [Roundtrip](references/roundtrip.md).

## What's next

- **P4** — Plugin marketplace, Document Standard ([roadmap](references/roadmap.md))

## Install

### Requirements

- **Python 3.10+**
- **pandoc 3.x** — only for `--engine pandoc` / `--preset wecom`

### Mermaid (`mmdc`)

Only needed when your Markdown contains ` ```mermaid ` code blocks **and** you want them rendered as images. Documents without Mermaid blocks do not require `mmdc`.

**Install** (requires Node.js / npm):

```bash
npm install -g @mermaid-js/mermaid-cli

# verify
mmdc --version
```

- **macOS:** run `brew install node` first if npm is not available
- **Linux:** install Node.js from your distribution, then run the command above

**Browser:** `mmdc` uses Puppeteer and needs a Chromium-based browser (Chrome, Edge, or Chromium). Alternatively, set `MD_TO_DOCX_BROWSER` or `PUPPETEER_EXECUTABLE_PATH` — see [Configuration](references/configuration.md).

**Without `mmdc`:**

| Condition | Result |
|-----------|--------|
| No Mermaid blocks | Unaffected |
| Native engine (default) + Mermaid | DOCX is produced; Mermaid shows as a **source code block** (stderr warning) |
| Native + `--strict-mermaid` | Conversion fails if `mmdc` is missing |
| `--engine pandoc` / `--preset wecom` + Mermaid | Conversion fails; install `mmdc` |
| Docker Playground (slim image) | Same as native degradation (code block) |

Rendered assets: native engine writes PNG/SVG to `{stem}-media/`; pandoc engine writes PNG to `{stem}mermaid图片/`.

See [Installation & troubleshooting](references/installation.md) for more.

### From source (recommended)

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert report.md
./bin/convert ./docs          # directory (recursive)
```

### Editable install (optional)

```bash
pip install -e .
pip install -e ".[mcp]"   # MCP server
pip install -e ".[web]"   # Playground API
```

PyPI package name: `md2docx-compiler` (console command remains `md-to-docx`).

## Run

```bash
# Convert a single file
python -m md_to_docx report.md

# Convert a directory (recursive)
python -m md_to_docx ./docs

# With options
python -m md_to_docx ./docs --exclude "README.md" --output-dir ./output

# Reverse: DOCX → Markdown
md-to-docx reverse report.docx -o report.md

# Diff two documents
md-to-docx diff v1.md v2.md --format md

# Custom plugin
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py
```

Subcommands: `convert` (default), `reverse`, `diff`. Legacy `md-to-docx file.md` still works.

CLI options:

- `--version` — Show version
- `--exclude PATTERN` — Exclude files matching pattern (can be used multiple times)
- `--output-dir DIR` — Write .docx files to a specific directory
- `--skip-existing` — Skip conversion if output already exists
- `--dry-run` — Preview what would be converted

By default, excludes `README.md`, `CHANGELOG.md`, `SKILL.md`, and `.github/**`. Automatically skips `.git` and `node_modules`.

## Documentation

- [Installation & troubleshooting](references/installation.md)
- [Presets](references/presets.md)
- [Validation](references/validation.md)
- [MCP server](references/mcp.md)
- [Use with AI agents](references/agents.md)
- [Web Playground](web/README.md)
- [Browser extension](browser-extension/README.md)
- [Examples gallery](examples/README.md)
- [Roundtrip / reverse / diff](references/roundtrip.md)
- [Plugin API](references/plugins.md)
- [GitHub Action](action/README.md)
- [Roadmap](references/roadmap.md)
- [Environment variables](references/configuration.md)
- [WeCom import guide](references/wecom-import.md)
- [Development & tests](references/development.md)

**Entry points:** Humans: `README.md` / `README.zh.md`; Cursor: [SKILL.md](SKILL.md); MCP: [references/mcp.md](references/mcp.md); Playground: [web/README.md](web/README.md); extension: [browser-extension/README.md](browser-extension/README.md).

## Cursor Skill

Symlink this repo to `~/.cursor/skills/md-to-docx` to use as a Cursor Agent skill:

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

See [SKILL.md](SKILL.md) for agent instructions.

## License

MIT — see [LICENSE](LICENSE).

---

## Star History

GitHub restricted public stargazer API access in 2026, so hosted `api.star-history.com` badges no longer work for most repos. This chart is generated by [`.github/workflows/star-history.yml`](.github/workflows/star-history.yml) and committed into the repo.

<!-- star-history:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/star-history/star-history-dark.svg">
  <img alt="Star history" src="assets/star-history/star-history-light.svg">
</picture>
<!-- star-history:end -->
