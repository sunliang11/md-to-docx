"""FastAPI Web Playground for md-to-docx."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from md_to_docx import __version__
from md_to_docx.api import convert
from md_to_docx.errors import MdToDocxError
from md_to_docx.mcp.handlers import PRESET_DESCRIPTIONS
from md_to_docx.presets_build import PRESET_SPECS
from md_to_docx.preset import PRESETS

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
EXAMPLES_DIR = REPO_ROOT / "examples"

MAX_BODY_BYTES = 400 * 1024
CONVERT_TIMEOUT_SEC = 30

PLAYGROUND_PRESET_ORDER = [
    "professional",
    "editorial",
    "technical",
    "academic",
    "business",
    "report",
]
PLAYGROUND_PRESETS = [n for n in PLAYGROUND_PRESET_ORDER if n in PRESETS]

EXAMPLE_FILES = {
    "technical-report": "technical-report/example.md",
    "academic-paper": "academic-paper/example.md",
    "business-report": "business-report/example.md",
    "meeting-notes": "meeting-notes/example.md",
    "api-document": "api-document/example.md",
    "ai-report": "ai-report/example.md",
    "chinese-report": "chinese-report/example.md",
}


class ConvertRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    preset: str = "technical"
    toc: bool | None = None


app = FastAPI(title="md-to-docx Playground", version=__version__)

# Production: restrict origins instead of *
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/api/convert":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "problem": "Request too large",
                    "cause": f"body exceeds {MAX_BODY_BYTES} bytes",
                    "fix": "Reduce markdown size below 400KB",
                },
            )
    return await call_next(request)


def _convert_sync(markdown: str, preset: str, toc: bool | None) -> Path:
    with tempfile.TemporaryDirectory(prefix="md_to_docx_web_") as tmp:
        work = Path(tmp)
        out = work / "document.docx"
        result = convert(
            markdown_text=markdown,
            output=out,
            preset=preset,
            toc=toc,
        )
        # Copy to a persistent temp file for FileResponse
        persistent = Path(tempfile.gettempdir()) / f"md_to_docx_{out.name}"
        persistent.write_bytes(result.output_path.read_bytes())
        return persistent


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    return {"ok": True, "version": __version__}


@app.get("/api/presets")
async def api_presets() -> dict[str, Any]:
    items = []
    for name in PLAYGROUND_PRESETS:
        preset = PRESETS[name]
        spec = PRESET_SPECS.get(name, {})
        preview = {
            "latin": spec.get("latin", "Calibri"),
            "east_asia": spec.get("east_asia", "Microsoft YaHei"),
            "body_pt": spec.get("body_pt", 11),
            "heading_color": "#" + spec.get("heading_color", "111827"),
            "header": spec.get("header"),
        }
        items.append(
            {
                "name": name,
                "engine": preset.engine,
                "toc": preset.toc,
                "numbering": preset.numbering,
                "description": PRESET_DESCRIPTIONS.get(name, ""),
                "preview": preview,
            }
        )
    return {"presets": items}


@app.post("/api/convert")
async def api_convert(body: ConvertRequest):
    if body.preset not in PLAYGROUND_PRESETS:
        raise HTTPException(
            status_code=400,
            detail={
                "problem": "Invalid preset",
                "cause": f"preset '{body.preset}' is not available in playground",
                "fix": f"Use one of: {', '.join(PLAYGROUND_PRESETS)}",
            },
        )
    if not body.markdown.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "problem": "Empty document",
                "cause": "markdown is empty",
                "fix": "Add content before generating DOCX",
            },
        )
    try:
        out_path = await asyncio.wait_for(
            run_in_threadpool(
                _convert_sync,
                body.markdown,
                body.preset,
                body.toc,
            ),
            timeout=CONVERT_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=500,
            detail={
                "problem": "Conversion timed out",
                "cause": f"exceeded {CONVERT_TIMEOUT_SEC}s",
                "fix": "Simplify document or reduce size",
            },
        )
    except MdToDocxError as exc:
        raise HTTPException(status_code=400, detail=exc.to_dict())
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "problem": "Conversion failed",
                "cause": str(exc),
                "fix": "Check markdown content and try again",
            },
        )

    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="document.docx",
        background=None,
    )


@app.get("/examples/{name}.md")
async def get_example(name: str):
    rel = EXAMPLE_FILES.get(name)
    if not rel:
        raise HTTPException(status_code=404, detail="example not found")
    path = EXAMPLES_DIR / rel
    if not path.is_file():
        raise HTTPException(status_code=404, detail="example file missing")
    return FileResponse(path, media_type="text/markdown; charset=utf-8")


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
