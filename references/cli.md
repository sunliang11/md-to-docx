English | [中文](cli.zh.md)

# CLI Reference

Complete command-line reference for **md-to-docx** — the open-source document compiler.

For project overview see [README.md](../README.md). For install troubleshooting see [installation.md](installation.md).

---

## Quick recipes

Copy-paste examples for common tasks.

```bash
# Convert a single file (technical report style)
md-to-docx report.md --preset technical


# Batch-convert a folder; write DOCX under dist/docx (keeps subfolders)
md-to-docx ./docs --output-dir ./dist/docx

# Preview which files would be converted (no output written)
md-to-docx ./docs --dry-run

# Use your own Word letterhead / styles
md-to-docx report.md --template letterhead.docx

# Validate Markdown only — no .docx created
md-to-docx report.md --check

# Word → Markdown (editable source for Git)
md-to-docx reverse report.docx -o report.md

# Compare two document versions (changelog-style output)
md-to-docx diff v1.md v2.md --format md

# Run from a git clone without pip install
./bin/convert report.md --preset technical

# After pip install — use md-to-docx from any directory
pip install -e .
md-to-docx report.md --preset professional
```

---

## How to run commands

There are several equivalent ways to invoke the same CLI. Pick one that fits your setup.

| Method | When to use | Example |
|--------|-------------|---------|
| **`bin/convert`** | Git clone or Cursor skill; **no pip** | `./bin/convert report.md` |
| **`pip install -e .`** | Put `md-to-docx` on your PATH globally | `md-to-docx report.md` |
| **`pip install -e ".[dev]"`** | Development + pytest | Same as above + test deps |
| **`pip install -e ".[mcp]"`** | MCP clients (Cursor, Claude Desktop) | Same CLI; run `md-to-docx mcp` |
| **`pip install "git+https://..."`** | Install without cloning locally | Remote editable install |
| **`python -m md_to_docx`** | Same as `md-to-docx`; works if PATH script missing | `python3 -m md_to_docx report.md` |
| **`PYTHONPATH=scripts python -m md_to_docx`** | Run from source tree (CI style) | No pip install needed |

### pip install step-by-step

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .              # base CLI: md-to-docx
# optional extras:
pip install -e ".[dev]"       # pytest, pillow
pip install -e ".[mcp]"       # MCP deps; start with: md-to-docx mcp
pip install -e ".[web]"       # Web Playground deps

# verify
which md-to-docx              # should print a path in your venv or ~/.local/bin
md-to-docx --version
```

> **Not on PyPI yet.** Package name is `md2docx-compiler`; the only CLI command is **`md-to-docx`**.  
> After `pip install -e .`, PATH gains a single script: **`md-to-docx`**. MCP is the subcommand `md-to-docx mcp` (requires `[mcp]` extra).

### Optional shell alias

Point an alias at `bin/convert` if you prefer a short name and always use the repo checkout:

```bash
# ~/.zshrc
alias md_to_docx="/path/to/md-to-docx/bin/convert"
```

All subcommands and flags work the same: `md_to_docx report.md`, `md_to_docx reverse …`, etc.

### Requirements (summary)

| Component | Required when |
|-----------|---------------|
| Python 3.10+ | Always |
| mmdc (Mermaid CLI) | Mermaid diagrams rendered as images |
| Chrome / Edge / Chromium | Mermaid rendering (used by mmdc) |

Details: [installation.md](installation.md).

---

## Command overview

```
md-to-docx [--version] [convert options] PATH     # default subcommand = convert
md-to-docx convert [options] PATH
md-to-docx reverse INPUT -o OUTPUT
md-to-docx diff A B [--format text|json|md]
md-to-docx build presets|all            # developer: rebuild templates
```

| Subcommand | Purpose |
|------------|---------|
| *(default)* / `convert` | Markdown → DOCX |
| `reverse` | DOCX → Markdown |
| `diff` | Structural diff of two documents (.md or .docx) |
| `build` | Rebuild bundled Word template assets |

Legacy form `md-to-docx file.md` (without `convert`) still works.

---

## `convert` — Markdown to DOCX

### Synopsis

```bash
md-to-docx [options] PATH
md-to-docx convert [options] PATH
```

**`PATH`** — A `.md` file or a directory. Directories are scanned recursively for `*.md`.

### Input & output

| Option | Default | Description |
|--------|---------|-------------|
| `PATH` | *(required)* | Markdown file or directory to convert |
| `--output-dir DIR` | beside source | Write all `.docx` files under `DIR`. When scanning a directory, relative subpaths are preserved (e.g. `docs/a/x.md` → `DIR/a/x.docx`) |
| `--exclude PATTERN` | see below | Skip files matching glob pattern. Repeatable |
| `--skip-existing` | off | Skip if output `.docx` already exists |
| `--dry-run` | off | Print planned conversions without writing files |

**Default exclusions** (directory scans only): `README.md`, `CHANGELOG.md`, `SKILL.md`, `.github/**`.  
**Always skipped directories:** `.git/`, `node_modules/`.

```bash
md-to-docx ./docs --output-dir ./output --exclude "*.draft.md"
md-to-docx ./docs --dry-run
md-to-docx report.md --skip-existing
```

### Engine & template

| Option | Default | Description |
|--------|---------|-------------|
| `--preset NAME` | none | Bundle template + flags. Values: `professional`, `technical`, `academic`, `business`, `report` |
| `--template PATH` | built-in reference | Custom `.docx` template |

**Preset defaults** (explicit CLI flags override preset):

| Preset | Engine | TOC | Numbering |
|--------|--------|-----|-----------|
| `professional` | native | yes | no |
| `technical` | native | yes | yes |
| `academic` | native | yes | yes |
| `business` | native | no | no |
| `report` | native | yes | no |

See [presets.md](presets.md) for font/style details.

```bash
md-to-docx report.md --preset technical
md-to-docx report.md --template templates/my-template/template.docx
md-to-docx report.md --template custom.docx
```

### Document structure

| Option | Default | Description |
|--------|---------|-------------|
| `--toc` | off (unless preset enables) | Insert Word table of contents |
| `--no-toc` | — | Disable TOC even if preset enables it |
| `--toc-title TEXT` | `Contents` | TOC heading text |
| `--numbering` | off (unless preset enables) | Chapter / heading numbering |
| `--no-page-numbers` | off | Omit page numbers in footer |

```bash
md-to-docx report.md --preset professional --toc --numbering
md-to-docx report.md --no-toc
```

### Document metadata

| Option | Default | Description |
|--------|---------|-------------|
| `--title TEXT` | from frontmatter | Document title |
| `--author TEXT` | from frontmatter | Author name |
| `--date TEXT` | from frontmatter | Date string |
| `--doc-version TEXT` | none | Version label in header/footer |

YAML frontmatter in the Markdown file is also read when flags are omitted.

### Caption & section labels

| Option | Default | Description |
|--------|---------|-------------|
| `--figure-label TEXT` | `Figure` | Prefix for figure captions |
| `--table-label TEXT` | `Table` | Prefix for table captions |
| `--section-label TEXT` | `Section` | Label for section cross-refs |

### Preprocessing & plugins

| Option | Default | Description |
|--------|---------|-------------|
| `--normalize` | on | Fix tables, lists, headings, code fences before convert |
| `--no-normalize` | — | Pass Markdown through unchanged |
| `--plugin PATH` | none | Load a Python transform plugin (repeatable) |
| `--no-plugins` | off | Disable built-in plugins (mermaid, math, captions) |

```bash
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py
md-to-docx report.md --no-plugins
```

See [plugins.md](plugins.md).

### Mermaid

| Option | Default | Description |
|--------|---------|-------------|
| `--strict-mermaid` | off | Fail if `mmdc` is missing and document contains Mermaid blocks |

Without `mmdc`, diagrams appear as source code blocks in the DOCX (conversion still succeeds unless `--strict-mermaid`).

### Validate mode (`--check`)

Run validation **without** generating a `.docx`.

| Option | Default | Description |
|--------|---------|-------------|
| `--check` | off | Validate only |
| `--check-format text\|json` | `text` | Output format |
| `--strict` | off | Treat warnings as errors |

```bash
md-to-docx report.md --check
md-to-docx report.md --check --check-format json
md-to-docx ./docs --check --strict
```

Validation rules: [validation.md](validation.md).

### Global convert flags

| Option | Description |
|--------|-------------|
| `--version` | Print version and exit |

---

## `reverse` — DOCX to Markdown

### Synopsis

```bash
md-to-docx reverse INPUT -o OUTPUT [options]
```

| Argument / option | Default | Description |
|-------------------|---------|-------------|
| `INPUT` | *(required)* | Source `.docx` file |
| `-o`, `--output PATH` | *(required)* | Output `.md` path |
| `--version` | — | Print version and exit |

```bash
md-to-docx reverse report.docx -o report.md
```

Support matrix and limitations: [roundtrip.md](roundtrip.md).

---

## `diff` — compare two documents

### Synopsis

```bash
md-to-docx diff A B [options]
```

| Argument / option | Default | Description |
|-------------------|---------|-------------|
| `A` | *(required)* | First document (`.md` or `.docx`) |
| `B` | *(required)* | Second document |
| `--format text\|json\|md` | `text` | Output format. `md` produces a changelog-style summary |
| `--version` | — | Print version and exit |

```bash
md-to-docx diff draft-v1.md draft-v2.md
md-to-docx diff old.docx new.docx --format json
md-to-docx diff a.md b.md --format md
```

---

## `build` — rebuild template assets (developers)

Rebuild bundled Word templates under `assets/`. Used when changing styles in Python build scripts or before a release.

```bash
md-to-docx build presets      # assets/presets/*.docx + reference-native.docx
md-to-docx build all          # same as presets
```

Requires `python-docx` (included in base dependencies).

Equivalent module invocations (CI/Docker still use these):

```bash
python -m md_to_docx.presets_build
```

---

## Environment variables

| Variable | Default | Purpose |
|----------|---------|-------------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | Mermaid PNG scale (higher = sharper, larger files) |
| `MD_TO_DOCX_MERMAID_WIDTH` | unset | Optional mmdc width in pixels (e.g. `1200`) |
| `MD_TO_DOCX_BROWSER` | auto-detect | Browser executable for mmdc |
| `PUPPETEER_EXECUTABLE_PATH` | auto-detect | Same as above (Puppeteer convention) |

```bash
MD_TO_DOCX_MERMAID_SCALE=5 md-to-docx report.md
```

More details: [configuration.md](configuration.md).

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success (or validate with warnings only) |
| `1` | Conversion/validation failure, or partial batch failure |
| `2` | Missing required argument or invalid usage |

---

## Troubleshooting

| Error / symptom | Likely cause | Fix |
|-----------------|--------------|-----|
| `path does not exist: …` | Wrong filename or path | Check spelling and extension (must be `.md` for single-file convert) |
| `not a Markdown file` | Path is not `.md` | Only `.md` files are converted |
| `no .md files found` | Empty directory or all files excluded | Run `--dry-run` to inspect; adjust `--exclude` |
| `Template not found` | Preset template missing from assets | Run `md-to-docx build presets` |
| Mermaid shows as code block | `mmdc` not installed | `npm install -g @mermaid-js/mermaid-cli` or use `--strict-mermaid` to fail loudly |
| `No module named md_to_docx` | Running without install or PYTHONPATH | Use `./bin/convert` or `pip install -e .` |

Full install guide: [installation.md](installation.md).

---

## Further reading

- [Presets](presets.md) — template styles per preset
- [Validation](validation.md) — `--check` rule codes
- [Roundtrip](roundtrip.md) — reverse & diff support matrix
- [Plugins](plugins.md) — custom `--plugin` transforms
- [MCP server](mcp.md) — `md-to-docx mcp` for AI clients
- [Configuration](configuration.md) — env vars and bundled assets
- [GitHub Action](../action/README.md) — CI automation
