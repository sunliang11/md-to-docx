English | [中文](README.zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml/badge.svg)](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

# md-to-docx

### The open-source document compiler for the AI era.

```
    AI / Markdown
          ↓
    Professional DOCX
```

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/sunliang11/md-to-docx?quickstart=1)
· [Install](#install)
· [GitHub](https://github.com/sunliang11/md-to-docx)

---

### Why md-to-docx?

- ✓ **AI → Word** — compile AI drafts into deliverable DOCX ([agents](references/agents.md))
- ✓ **Markdown → DOCX** — `md-to-docx report.md --preset technical`
- ✓ **DOCX → Markdown** — `md-to-docx reverse report.docx -o report.md`
- ✓ **Document Diff** — structural compare for `.md` and `.docx` ([roundtrip](references/roundtrip.md))
- ✓ **Templates** — presets + community Word templates ([presets](references/presets.md) · [templates](templates/README.md))
- ✓ **MCP** — convert, validate, apply_template, list_presets ([mcp](references/mcp.md))
- ✓ **Cursor / Claude / Codex / Gemini** — [SKILL.md](SKILL.md) · [skills/](skills/)
- ✓ **Browser Extension** — export ChatGPT / Claude / Gemini chats ([extension](browser-extension/README.md))
- ✓ **GitHub Action** — CI builds DOCX from Markdown ([action](action/README.md))
- ✓ **Local & Private** — no API keys, self-host with Docker or Codespaces

---

### 30 seconds demo

```
input.md  →  md-to-docx  →  report.docx
```

```bash
./bin/convert examples/technical-report/example.md --preset technical
```

![Convert Markdown to DOCX](assets/demo/hero.gif)

**Before** (Markdown) → **After** (Word)

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">

---

### AI Workflow

```
ChatGPT · Claude · Cursor · Codex · Gemini
                  ↓
              md-to-docx
                  ↓
         Professional Word
```

[SKILL.md](SKILL.md) · [Use with AI agents](references/agents.md) · [MCP server](references/mcp.md)

---

### Templates

[Technical](examples/technical-report/) · [Business](examples/business-report/) · [Academic](examples/academic-paper/) · [Chinese](examples/chinese-report/) · [API](examples/api-document/) · [Meeting](examples/meeting-notes/)

See the full [examples gallery](examples/README.md).

---

### Ecosystem

[CLI](references/cli.md) · [MCP](references/mcp.md) · [VS Code](editors/vscode/README.md) · [Obsidian](editors/obsidian/README.md) · [Browser](browser-extension/README.md) · [GitHub Action](action/README.md) · [Docker](web/README.md)

---

## Quick Start

**Option A — Git clone (recommended, no pip)**

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md --preset technical
```

**Option B — Docker Playground (no local Python)**

```bash
docker compose -f web/docker-compose.yml up --build
# open http://localhost:8080
```

**Option C — GitHub Codespaces (zero local install)**

Click **Open in GitHub Codespaces** above — the Web Playground starts on port 8080 automatically.

**Option D — Local Web Playground (pip + uvicorn)**

```bash
pip install -e ".[web]"
PYTHONPATH=scripts python -m md_to_docx.presets_build
uvicorn web.app:app --reload --port 8080
# open http://localhost:8080
```

## Commands

```bash
md-to-docx report.md --preset technical                              # convert (default)
md-to-docx reverse report.docx -o report.md                           # DOCX → Markdown
md-to-docx diff draft-v1.md draft-v2.md --format md                  # structural diff
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py   # custom plugin
md-to-docx report.md --check                                         # validate only
```

**Full option reference → [references/cli.md](references/cli.md)** (all subcommands, flags, install methods, and troubleshooting).

Subcommands: `convert` (default), `reverse`, `diff`, `build`. Legacy `md-to-docx file.md` still works.

**Batch & directories**

```bash
md-to-docx ./docs --output-dir ./output --exclude "README.md"
md-to-docx ./docs --dry-run
```

## What you can do

| What | One-liner | Try |
|------|-----------|-----|
| **Convert** | Compile Markdown or AI drafts into professional DOCX | `md-to-docx report.md --preset technical` |
| **Reverse** | Turn DOCX back into editable Markdown (native AST) | `md-to-docx reverse report.docx -o report.md` |
| **Diff** | Compare two versions by document structure (.md or .docx) | `md-to-docx diff v1.md v2.md --format md` |
| **Validate** | Lint Markdown before shipping — no DOCX output | `md-to-docx report.md --check` |
| **Extend** | Hook custom transforms with a small Python plugin | `md-to-docx report.md --plugin my_plugin.py` |
| **Automate (CI)** | Build DOCX in GitHub Actions; keep `.md` in Git | `uses: sunliang11/md-to-docx/action@v3` |
| **Editor export** | Right-click in VS Code or Obsidian → export Word | [VS Code](editors/vscode/README.md) · [Obsidian](editors/obsidian/README.md) |
| **AI agents** | Cursor / MCP / browser — local, no API keys | [SKILL.md](SKILL.md) · [MCP](references/mcp.md) |

**Pipeline:** Markdown / AI output → Document AST → Professional DOCX (and back).

## Choose how to run it

| Entry | One-liner | Doc |
|-------|-----------|-----|
| CLI | Full command-line tool (`md-to-docx`) | [CLI Reference](references/cli.md) |
| `bin/convert` | Run from a git clone without `pip install` | — |
| Python API | `from md_to_docx.api import convert` for scripts | [development.md](references/development.md) |
| Cursor Skill | Agent picks a preset and converts for you | [SKILL.md](SKILL.md) |
| Claude / Codex / Gemini | Platform-specific skill copies | [skills/](skills/) |
| MCP | Four tools: convert, validate, apply_template, list_presets | [mcp.md](references/mcp.md) |
| Web Playground | Edit in browser, download DOCX (Docker / Codespaces) | [web/README.md](web/README.md) |
| Browser extension | Export ChatGPT / Claude / Gemini chats to Word | [browser-extension/README.md](browser-extension/README.md) |
| VS Code | Command `MD: Export to DOCX` on Markdown files | [editors/vscode/README.md](editors/vscode/README.md) |
| Obsidian | `Export to Professional Word` (desktop only) | [editors/obsidian/README.md](editors/obsidian/README.md) |
| GitHub Action | CI builds DOCX from Markdown | [action/README.md](action/README.md) |

## Document support

- **Native AST engine** — Document AST → professional DOCX
- **Structure** — headings, lists, tables, code, blockquotes, images, footnotes, task lists
- **CJK** — Microsoft YaHei / SimSun templates
- **Mermaid** — PNG when `mmdc` is installed; degrades to code block otherwise
- **Math** — basic LaTeX → OMML
- **Captions & cross-refs** — `{#fig:id}`, `[@fig:id]`, table captions
- **TOC & page numbers** — Word-native fields, header/footer
- **Page breaks** — `<!-- pagebreak -->` in Markdown
- **Frontmatter** — YAML metadata (title, author, date, …)

See [presets](references/presets.md), [roundtrip](references/roundtrip.md), [plugins](references/plugins.md).

## Examples

Seven ready-made reports in [examples/](examples/README.md): technical, business, academic, API, meeting notes, AI report, Chinese report — each with `example.md` and compiled `example.docx`. Plugin sample: [examples/plugins/](examples/plugins/).

## Git workflow

Keep **Markdown in Git**; treat **DOCX as a build artifact**:

```gitignore
dist/docx/
*.docx
```

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

See [action/README.md](action/README.md). Roadmap: [references/roadmap.md](references/roadmap.md).

## Community templates

Browse contributed Word templates in [`templates/`](templates/README.md). Use any template with `--template`:

```bash
md-to-docx report.md --template templates/technical-design/template.docx
```

To contribute a template, see the PR checklist in [templates/README.md](templates/README.md). Document syntax: [spec/document-markdown.md](spec/document-markdown.md) (ODM `odm-0.1`).

## Install

### Requirements

- **Python 3.10+**
- **mmdc** — only if you need Mermaid rendered as images ([installation.md](references/installation.md))

### From source (development)

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e ".[dev]"      # or -e ".[mcp]" / -e ".[web]"
which md-to-docx             # verify CLI is on PATH
md-to-docx report.md         # or ./bin/convert report.md (no pip)
```

Install options and entry points: [CLI Reference — How to run commands](references/cli.md#how-to-run-commands).

**Not on PyPI yet.** Planned package name: `md2docx-compiler` · CLI command: `md-to-docx`. Install from source or `pip install "git+https://github.com/sunliang11/md-to-docx.git"`.

**Mermaid note:** Without `mmdc`, diagrams appear as source code blocks. Use `--strict-mermaid` to fail instead. Full matrix: [installation.md](references/installation.md).

## Documentation

- **[CLI Reference](references/cli.md)** — all commands, flags, install methods
- [Installation & troubleshooting](references/installation.md)
- [Presets](references/presets.md)
- [Validation](references/validation.md)
- [Roundtrip / reverse / diff](references/roundtrip.md)
- [Plugin API](references/plugins.md)
- [MCP server](references/mcp.md)
- [Use with AI agents](references/agents.md)
- [GitHub Action](action/README.md)
- [Web Playground](web/README.md)
- [Browser extension](browser-extension/README.md)
- [VS Code extension](editors/vscode/README.md)
- [Obsidian plugin](editors/obsidian/README.md)
- [Examples gallery](examples/README.md)
- [Example plugins](examples/plugins/)
- [Environment variables](references/configuration.md)
- [Contributing](CONTRIBUTING.md)
- [Development & tests](references/development.md)
- [Release process](references/release.md)
- [Roadmap](references/roadmap.md)

## Cursor Skill

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
