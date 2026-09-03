"""FastAPI Web Playground for md-to-docx."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from md_to_docx import __version__
from md_to_docx.api import ConvertOptions, apply_preset, validate_markdown
from md_to_docx.converter import convert_file
from md_to_docx.diff import diff_documents, format_diff
from md_to_docx.errors import MdToDocxError
from md_to_docx.load import load_document
from md_to_docx.mcp.handlers import PRESET_DESCRIPTIONS
from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.paths import native_reference_doc
from md_to_docx.preset import PRESETS
from md_to_docx.presets_build import PRESET_SPECS
from md_to_docx.render.html import CALLOUT_CSS, render_html
from md_to_docx.reverse import reverse_docx
from md_to_docx.transform.numbering import apply_heading_numbers

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
EXAMPLES_DIR = REPO_ROOT / "examples"
TEMPLATES_DIR = REPO_ROOT / "templates"

MAX_BODY_BYTES = 400 * 1024
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
CONVERT_TIMEOUT_SEC = 30
PREVIEW_TIMEOUT_SEC = 15

PLAYGROUND_PRESET_ORDER = [
    "professional",
    "editorial",
    "technical",
    "academic",
    "business",
    "report",
]
PLAYGROUND_PRESETS = [n for n in PLAYGROUND_PRESET_ORDER if n in PRESETS]

COMMUNITY_TEMPLATES: dict[str, Path] = {
    "technical-design": TEMPLATES_DIR / "technical-design" / "template.docx",
    "consulting-report": TEMPLATES_DIR / "consulting-report" / "template.docx",
    "academic-ieee-ish": TEMPLATES_DIR / "academic-ieee-ish" / "template.docx",
    "chinese-official": TEMPLATES_DIR / "chinese-official" / "template.docx",
}

TEMPLATE_LABELS = {
    "technical-design": "Technical design",
    "consulting-report": "Consulting report",
    "academic-ieee-ish": "Academic (IEEE-ish)",
    "chinese-official": "Chinese official",
}

EXAMPLE_FILES = {
    "technical-report": "technical-report/example.md",
    "academic-paper": "academic-paper/example.md",
    "business-report": "business-report/example.md",
    "meeting-notes": "meeting-notes/example.md",
    "api-document": "api-document/example.md",
    "ai-report": "ai-report/example.md",
    "chinese-report": "chinese-report/example.md",
}

DiffFormat = Literal["text", "json", "md"]


class ConvertRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    preset: str = "technical"
    toc: bool | None = None
    numbering: bool | None = None
    title: str | None = None
    author: str | None = None
    date: str | None = None
    page_numbers: bool = True
    template: str | None = None


class PreviewRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    numbering: bool = False


class ValidateRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    strict: bool = False


class DiffRequest(BaseModel):
    a: str = Field(..., max_length=MAX_BODY_BYTES)
    b: str = Field(..., max_length=MAX_BODY_BYTES)
    format: DiffFormat = "md"


app = FastAPI(title="md-to-docx Playground", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _detail(problem: str, cause: str, fix: str) -> dict[str, str]:
    return {"problem": problem, "cause": cause, "fix": fix}


def _http_error(status: int, problem: str, cause: str, fix: str) -> None:
    raise HTTPException(status_code=status, detail=_detail(problem, cause, fix))


def _resolve_template(key: str | None) -> Path | None:
    if not key:
        return None
    path = COMMUNITY_TEMPLATES.get(key)
    if path is None or not path.is_file():
        _http_error(
            400,
            "Invalid template",
            f"template '{key}' is not available",
            "Use a community template from the list, or leave it empty",
        )
    return path


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    if request.method == "POST" and request.url.path in {
        "/api/convert",
        "/api/preview",
        "/api/validate",
        "/api/diff",
    }:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_BYTES + 4096:
            return JSONResponse(
                status_code=413,
                content=_detail(
                    "Request too large",
                    f"body exceeds {MAX_BODY_BYTES} bytes",
                    "Reduce markdown size below 400KB",
                ),
            )
    return await call_next(request)


def _html_fragment(document) -> tuple[str, str]:
    full = render_html(document)
    start = full.find("<body>")
    end = full.rfind("</body>")
    if start >= 0 and end > start:
        body = full[start + len("<body>") : end].strip()
    else:
        body = full
    return body, CALLOUT_CSS


def _convert_sync(
    markdown: str,
    preset: str,
    toc: bool | None,
    numbering: bool | None,
    title: str | None,
    author: str | None,
    date: str | None,
    page_numbers: bool,
    template_path: Path | None,
) -> Path:
    options = ConvertOptions(
        toc=toc,
        numbering=False,
        title=title,
        author=author,
        date=date,
        page_numbers=page_numbers,
    )
    options = apply_preset(preset, options)
    if toc is not None:
        options.toc = toc
    if numbering is not None:
        options.numbering = numbering
    if template_path is not None:
        options.template = template_path
    if options.toc is None:
        options.toc = False
    if options.template is None:
        options.template = native_reference_doc()

    with tempfile.TemporaryDirectory(prefix="md_to_docx_web_") as tmp:
        work = Path(tmp)
        md_path = work / "document.md"
        md_path.write_text(markdown, encoding="utf-8")
        out = work / "document.docx"
        convert_file(
            md_path,
            out,
            template_path=options.template,
            toc=options.toc,
            toc_title=options.toc_title,
            numbering=options.numbering,
            title=options.title,
            author=options.author,
            date=options.date,
            page_numbers=options.page_numbers,
            figure_label=options.figure_label,
            table_label=options.table_label,
            section_label=options.section_label,
        )
        persistent = Path(tempfile.gettempdir()) / "md_to_docx_document.docx"
        persistent.write_bytes(out.read_bytes())
        return persistent


def _preview_sync(markdown: str, numbering: bool) -> dict[str, str]:
    doc = parse_markdown(markdown, source_path=Path("input.md"))
    doc = apply_heading_numbers(doc, enabled=numbering)
    html, css = _html_fragment(doc)
    return {"html": html, "css": css}


def _reverse_sync(data: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="md_to_docx_rev_") as tmp:
        work = Path(tmp)
        src = work / "input.docx"
        out = work / "output.md"
        src.write_bytes(data)
        reverse_docx(src, out)
        return out.read_text(encoding="utf-8")


def _diff_from_text(a: str, b: str, fmt: str) -> str:
    with tempfile.TemporaryDirectory(prefix="md_to_docx_diff_") as tmp:
        work = Path(tmp)
        pa = work / "a.md"
        pb = work / "b.md"
        pa.write_text(a, encoding="utf-8")
        pb.write_text(b, encoding="utf-8")
        changes = diff_documents(load_document(pa), load_document(pb))
        return format_diff(changes, fmt=fmt)


def _diff_from_files(path_a: Path, path_b: Path, fmt: str) -> str:
    changes = diff_documents(load_document(path_a), load_document(path_b))
    return format_diff(changes, fmt=fmt)


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
                "toc": preset.toc,
                "numbering": preset.numbering,
                "description": PRESET_DESCRIPTIONS.get(name, ""),
                "preview": preview,
            }
        )
    return {"presets": items}


@app.get("/api/templates")
async def api_templates() -> dict[str, Any]:
    items = []
    for key, path in COMMUNITY_TEMPLATES.items():
        if path.is_file():
            items.append({"id": key, "name": TEMPLATE_LABELS.get(key, key)})
    return {"templates": items}


@app.post("/api/preview")
async def api_preview(body: PreviewRequest):
    if not body.markdown.strip():
        return {"html": "", "css": CALLOUT_CSS}
    try:
        return await asyncio.wait_for(
            run_in_threadpool(_preview_sync, body.markdown, body.numbering),
            timeout=PREVIEW_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        _http_error(
            500,
            "Preview timed out",
            f"exceeded {PREVIEW_TIMEOUT_SEC}s",
            "Simplify the document",
        )
    except Exception as exc:
        _http_error(
            400,
            "Preview failed",
            str(exc),
            "Check markdown syntax and try again",
        )


@app.post("/api/validate")
async def api_validate(body: ValidateRequest):
    issues = validate_markdown(body.markdown, strict=body.strict)
    return {
        "ok": not any(i.severity == "error" for i in issues),
        "issues": [
            {
                "severity": i.severity,
                "code": i.code,
                "message": i.message,
                "line": i.line,
            }
            for i in issues
        ],
    }


@app.post("/api/convert")
async def api_convert(body: ConvertRequest):
    if body.preset not in PLAYGROUND_PRESETS:
        _http_error(
            400,
            "Invalid preset",
            f"preset '{body.preset}' is not available in playground",
            f"Use one of: {', '.join(PLAYGROUND_PRESETS)}",
        )
    if not body.markdown.strip():
        _http_error(
            400,
            "Empty document",
            "markdown is empty",
            "Add content before generating DOCX",
        )
    try:
        out_path = await asyncio.wait_for(
            run_in_threadpool(
                _convert_sync,
                body.markdown,
                body.preset,
                body.toc,
                body.numbering,
                body.title,
                body.author,
                body.date,
                body.page_numbers,
                _resolve_template(body.template),
            ),
            timeout=CONVERT_TIMEOUT_SEC,
        )
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        _http_error(
            500,
            "Conversion timed out",
            f"exceeded {CONVERT_TIMEOUT_SEC}s",
            "Simplify document or reduce size",
        )
    except MdToDocxError as exc:
        raise HTTPException(status_code=400, detail=exc.to_dict())
    except Exception as exc:
        _http_error(
            500,
            "Conversion failed",
            str(exc),
            "Check markdown content and try again",
        )

    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="document.docx",
        background=None,
    )


async def _read_upload(
    file: UploadFile,
    *,
    allowed: tuple[str, ...],
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> bytes:
    name = (file.filename or "").lower()
    if not any(name.endswith(ext) for ext in allowed):
        _http_error(
            400,
            "Unsupported file",
            f"got '{file.filename or ''}'",
            f"Upload a file ending with {', '.join(allowed)}",
        )
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        _http_error(
            413,
            "Request too large",
            f"file exceeds {max_bytes} bytes",
            "Use a smaller document (max 2MB)",
        )
    if not data:
        _http_error(400, "Empty file", "upload was empty", "Choose a non-empty file")
    return data


@app.post("/api/reverse")
async def api_reverse(file: UploadFile = File(...)):
    data = await _read_upload(file, allowed=(".docx",))
    try:
        text = await asyncio.wait_for(
            run_in_threadpool(_reverse_sync, data),
            timeout=CONVERT_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        _http_error(
            500,
            "Reverse timed out",
            f"exceeded {CONVERT_TIMEOUT_SEC}s",
            "Try a smaller DOCX",
        )
    except Exception as exc:
        _http_error(
            400,
            "Reverse failed",
            str(exc),
            "Upload a valid .docx produced by Word or md-to-docx",
        )
    return PlainTextResponse(text, media_type="text/markdown; charset=utf-8")


@app.post("/api/diff")
async def api_diff(body: DiffRequest):
    try:
        text = await asyncio.wait_for(
            run_in_threadpool(_diff_from_text, body.a, body.b, body.format),
            timeout=CONVERT_TIMEOUT_SEC,
        )
    except asyncio.TimeoutError:
        _http_error(
            500,
            "Diff timed out",
            f"exceeded {CONVERT_TIMEOUT_SEC}s",
            "Use shorter documents",
        )
    except Exception as exc:
        _http_error(
            400,
            "Diff failed",
            str(exc),
            "Provide two Markdown documents",
        )
    return PlainTextResponse(text, media_type="text/plain; charset=utf-8")


@app.post("/api/diff/files")
async def api_diff_files(
    a: UploadFile = File(...),
    b: UploadFile = File(...),
    format: DiffFormat = "md",
):
    data_a = await _read_upload(a, allowed=(".md", ".docx"))
    data_b = await _read_upload(b, allowed=(".md", ".docx"))
    name_a = a.filename or "a.md"
    name_b = b.filename or "b.md"

    def _run() -> str:
        with tempfile.TemporaryDirectory(prefix="md_to_docx_diffu_") as tmp:
            work = Path(tmp)
            pa = work / name_a
            pb = work / name_b
            pa.write_bytes(data_a)
            pb.write_bytes(data_b)
            return _diff_from_files(pa, pb, format)

    try:
        text = await asyncio.wait_for(run_in_threadpool(_run), timeout=CONVERT_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        _http_error(
            500,
            "Diff timed out",
            f"exceeded {CONVERT_TIMEOUT_SEC}s",
            "Use shorter documents",
        )
    except Exception as exc:
        _http_error(
            400,
            "Diff failed",
            str(exc),
            "Use .md or .docx files",
        )
    return PlainTextResponse(text, media_type="text/plain; charset=utf-8")


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
