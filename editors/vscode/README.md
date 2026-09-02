# VS Code Extension — md-to-docx

Export the current Markdown file to Word using the **md-to-docx** CLI on your machine.

## Prerequisites

```bash
pip install md2docx-compiler
# or from this repo:
pip install -e /path/to/md-to-docx
```

Ensure `md-to-docx` is on your `PATH`, or set **md-to-docx.path** in VS Code settings.

## Usage

- **Command Palette:** `MD: Export to DOCX`
- **Editor context menu:** right-click in a `.md` file → **MD: Export to DOCX**

Output is written beside the source file (or to **md-to-docx.outputDir** if set).

## Development

```bash
cd editors/vscode
npm install
npm run compile
```

Press **F5** in VS Code to launch an Extension Development Host.

## Package

```bash
npm install -g @vscode/vsce
vsce package
```

Produces `md-to-docx-0.1.0.vsix` for local install. Not published to the Marketplace by default.

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `md-to-docx.path` | `md-to-docx` | CLI executable |
| `md-to-docx.preset` | `technical` | `--preset` value |
| `md-to-docx.extraArgs` | `[]` | Extra CLI flags |
| `md-to-docx.outputDir` | `""` | Optional `--output-dir` |
