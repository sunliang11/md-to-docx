# Web Playground

Try md-to-docx in your browser — convert AI Markdown to DOCX without installing Python locally.

## Quick start (GitHub Codespaces)

From the [README](../README.md), click **Open in GitHub Codespaces**. The devcontainer installs web dependencies, builds presets, and starts the playground on port **8080** (forwarded automatically).

## Quick start (Docker)

From the repository root:

```bash
docker compose -f web/docker-compose.yml up --build
```

Open [http://localhost:8080](http://localhost:8080).

## Local dev (no Docker)

```bash
pip install -e ".[web]"
PYTHONPATH=scripts python -m md_to_docx.presets_build
uvicorn web.app:app --reload --port 8080
```

## Modules

Four top-level tasks (each has its own toolbar + workspace):

| Module | Job | Main input |
|--------|-----|------------|
| **To Word** | One Markdown → one DOCX | Upload `.md` (default) or paste; style preset; export |
| **Batch** | Many Markdown / zip → ZIP of DOCX | Drop multiple `.md` or one `.zip`; preview list or download |
| **From Word** | DOCX → Markdown | Drop `.docx` |
| **Compare** | Structural diff | Upload A/B (`.md` / `.docx`) or paste |

Advanced convert options (metadata, caption labels, normalize, plugins, community or uploaded Word template, strict check) live under **More options** — not on the first screen.

## Features

- Upload-first flows with drag-and-drop; paste as a secondary path
- Presets, TOC / numbering, community templates **or** upload your own `.docx` template
- Validate / check (optional strict mode) on To Word
- Batch: exclude globs, skip-existing, dry-run (“Preview list”), ZIP download
- Example documents from `examples/`
- Footer links to MCP, GitHub Action, and editor integrations (not run in the browser)

Preview is an AST HTML approximation, not Word layout.

## Limits

- Markdown body max **400KB**
- Single upload (reverse / template / diff file) max **2MB**
- Batch upload total max **10MB**, up to **50** Markdown files
- Conversion timeout **30s** (batch **90s**)
- Documents converted in temp storage and not persisted

## Mermaid

The default **slim** Docker image does not include `mmdc`. Mermaid blocks render as code in slim builds.

For flowchart rendering, build the full image:

```bash
docker build -f web/Dockerfile.full -t md-to-docx-playground-full .
docker run --rm -p 8080:8080 md-to-docx-playground-full
```

## Browser extension

The [browser extension](../browser-extension/README.md) POSTs to `http://127.0.0.1:8080/api/convert` by default.

## Privacy

Documents are converted in memory/temp and deleted. Self-host with Docker.
