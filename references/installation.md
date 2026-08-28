# Installation

See [README.md](../README.md) for a project overview.

## Requirements

| Component | Version | Required when |
|-----------|---------|---------------|
| **Python** | **3.10+** | Always (see `requires-python` in `pyproject.toml`) |
| **pandoc** | 3.x (Lua filters recommended) | Always |
| **@mermaid-js/mermaid-cli** (`mmdc`) | Latest stable | Markdown files contain ` ```mermaid ` blocks |
| **Chrome / Edge / Chromium** | Any recent version | Mermaid rendering (`mmdc` uses a browser) |
| **python-docx** | 1.0+ | Rebuilding the Word reference template only |

## Install the Python package

From a cloned repository:

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .
```

Or install directly from GitHub (replace the URL if you use a fork):

```bash
pip install "git+https://github.com/sunliang11/md-to-docx.git"
```

## Install system dependencies

### macOS

```bash
brew install pandoc
npm install -g @mermaid-js/mermaid-cli
```

### Linux

Install `pandoc` from your distribution or [pandoc.org](https://pandoc.org/installing.html), then:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Ensure a Chromium-based browser is installed, or set `MD_TO_DOCX_BROWSER` / `PUPPETEER_EXECUTABLE_PATH`.

## Install as a Cursor skill

Clone the repo, then symlink the repository root into your personal skills directory. The folder name must match the skill `name` (`md-to-docx`):

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

If you previously used `~/.cursor/skills/md_to_docx` (underscore), remove or replace that symlink.

## Verify installation

```bash
python3 --version          # must be 3.10+
which pandoc
python3 -m md_to_docx --help
```

Convert a sample file:

```bash
python3 -m md_to_docx tests/fixtures/sample.md
```

## Common errors

| Error | Fix |
|-------|-----|
| `` `pandoc` not found on PATH `` | Install pandoc and ensure it is on your `PATH` |
| `` `mmdc` not found `` | `npm install -g @mermaid-js/mermaid-cli` |
| `mmdc failed` / browser errors | Install Chrome/Chromium or set `MD_TO_DOCX_BROWSER` |
| `reference doc missing` | Run `python3 -m md_to_docx.reference` or `md-to-docx-build-reference` |
| `Python 3.9` or older | Upgrade to Python 3.10+ |
