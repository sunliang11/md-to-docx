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

- Left: Markdown editor. Right: HTML preview (approximation, not Word layout).
- Preset selector (native presets only; `wecom` requires pandoc and is not in the dropdown).
- **Generate DOCX** downloads `document.docx`.
- **Copy CLI command** for the equivalent `bin/convert` invocation.
- Example documents from `examples/`.

## Limits

- Markdown body max **400KB**
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
