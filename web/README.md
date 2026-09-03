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

## Features

- **Convert** — Markdown editor, engine HTML preview (callouts, math, page breaks, Mermaid source), presets, TOC / numbering / metadata, community Word templates, ODM syntax inserts, **Validate**, export DOCX, Copy CLI
- **Reverse** — upload `.docx` (max 2MB) → Markdown; copy or send to Convert
- **Diff** — two Markdown (or uploaded `.md` / `.docx`) documents, output `md` / `text` / `json`
- Example documents from `examples/`
- Footer links to MCP, GitHub Action, and editor integrations (not run in the browser)

Preview is an AST HTML approximation, not Word layout.

## Limits

- Markdown body max **400KB**
- Upload (reverse / diff files) max **2MB**
- Conversion timeout **30 seconds**
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
