# Obsidian Plugin — md-to-docx

Export vault Markdown to professional Word using the **md-to-docx** CLI (desktop only).

## Prerequisites

```bash
pip install md2docx-compiler
```

`md-to-docx` must be on your system `PATH`.

## Install (manual)

1. Copy this folder to `.obsidian/plugins/md-to-docx/` in your vault
2. Enable **md-to-docx** in Obsidian → Settings → Community plugins

Files needed:

- `manifest.json`
- `main.js`

## Commands

| Command | Description |
|---------|-------------|
| Export to Professional Word | Export the active note |
| Export folder to DOCX | Export all Markdown under vault root |

Output `.docx` files are written beside each `.md` file (or to a configured output folder via plugin data).

## Mobile

Not supported — Obsidian mobile cannot spawn the CLI. You'll see a desktop-only notice.

## Git workflow

Consider adding `*.docx` to your vault `.gitignore` if DOCX files are build artifacts.

## Configuration

Plugin data (optional, via Obsidian plugin data API):

```json
{
  "cli": "md-to-docx",
  "preset": "technical",
  "outputDir": "docx"
}
```

Set via Obsidian developer tools or a future settings tab.
