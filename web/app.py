"""FastAPI Web Playground for md-to-docx."""

from __future__ import annotations

import asyncio
import io
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from md_to_docx import __version__
from md_to_docx.api import ConvertOptions, apply_preset, validate_markdown
from md_to_docx.converter import collect_md_files, convert_file
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
MAX_BATCH_BYTES = 10 * 1024 * 1024
MAX_BATCH_FILES = 50
CONVERT_TIMEOUT_SEC = 30
BATCH_TIMEOUT_SEC = 90
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
CheckFormat = Literal["text", "json"]


class ConvertRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    preset: str = "technical"
    toc: bool | None = None
    numbering: bool | None = None
    toc_title: str | None = None
    title: str | None = None
    author: str | None = None
    date: str | None = None
    doc_version: str | None = None
    page_numbers: bool = True
    template: str | None = None
    figure_label: str | None = None
    table_label: str | None = None
    section_label: str | None = None
    normalize: bool = True
    no_plugins: bool = False
    strict_mermaid: bool = False


class PreviewRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    numbering: bool = False


class ValidateRequest(BaseModel):
    markdown: str = Field(..., max_length=MAX_BODY_BYTES)
    strict: bool = False
    format: CheckFormat = "json"


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


def _resolve_community_template(key: str | None) -> Path | None:
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


def _build_convert_options(
    *,
    preset: str,
    toc: bool | None,
    numbering: bool | None,
    toc_title: str | None,
    title: str | None,
    author: str | None,
    date: str | None,
    doc_version: str | None,
    page_numbers: bool,
    template_path: Path | None,
    figure_label: str | None,
    table_label: str | None,
    section_label: str | None,
    normalize: bool,
    no_plugins: bool,
    strict_mermaid: bool,
) -> ConvertOptions:
    options = ConvertOptions(
        toc=toc,
        numbering=False,
        title=title,
        author=author,
        date=date,
        doc_version=doc_version,
        page_numbers=page_numbers,
        normalize=normalize,
        strict_mermaid=strict_mermaid,
    )
    options = apply_preset(preset, options)
    if toc is not None:
        options.toc = toc
    if numbering is not None:
        options.numbering = numbering
    if toc_title is not None and toc_title.strip():
        options.toc_title = toc_title.strip()
    if figure_label is not None and figure_label.strip():
        options.figure_label = figure_label.strip()
    if table_label is not None and table_label.strip():
        options.table_label = table_label.strip()
    if section_label is not None and section_label.strip():
        options.section_label = section_label.strip()
    if template_path is not None:
        options.template = template_path
    if options.toc is None:
        options.toc = False
    if options.template is None:
        options.template = native_reference_doc()
    # Stash no_plugins on a private attr via return tuple — ConvertOptions has no field.
    return options


def _convert_with_options(
    markdown: str,
    options: ConvertOptions,
    *,
    no_plugins: bool = False,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="md_to_docx_web_") as tmp:
        work = Path(tmp)
        md_path = work / "document.md"
        md_path.write_text(markdown, encoding="utf-8")
        out = work / "document.docx"
        convert_file(
            md_path,
            out,
            template_path=options.template,
            toc=bool(options.toc),
            toc_title=options.toc_title,
            numbering=options.numbering,
            title=options.title,
            author=options.author,
            date=options.date,
            doc_version=options.doc_version,
            page_numbers=options.page_numbers,
            figure_label=options.figure_label,
            table_label=options.table_label,
            section_label=options.section_label,
            normalize=options.normalize,
            strict_mermaid=options.strict_mermaid,
            no_plugins=no_plugins,
        )
        persistent = Path(tempfile.gettempdir()) / "md_to_docx_document.docx"
        persistent.write_bytes(out.read_bytes())
        return persistent


def _convert_sync(
    markdown: str,
    preset: str,
    toc: bool | None,
    numbering: bool | None,
    toc_title: str | None,
    title: str | None,
    author: str | None,
    date: str | None,
    doc_version: str | None,
    page_numbers: bool,
    template_path: Path | None,
    figure_label: str | None,
    table_label: str | None,
    section_label: str | None,
    normalize: bool,
    no_plugins: bool,
    strict_mermaid: bool,
) -> Path:
    options = _build_convert_options(
        preset=preset,
        toc=toc,
        numbering=numbering,
        toc_title=toc_title,
        title=title,
        author=author,
        date=date,
        doc_version=doc_version,
        page_numbers=page_numbers,
        template_path=template_path,
        figure_label=figure_label,
        table_label=table_label,
        section_label=section_label,
        normalize=normalize,
        no_plugins=no_plugins,
        strict_mermaid=strict_mermaid,
    )
    return _convert_with_options(markdown, options, no_plugins=no_plugins)


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
            ctype = request.headers.get("content-type", "")
            # Multipart convert can be larger (template upload); skip JSON-only limit.
            if "multipart/form-data" not in ctype:
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


def _format_validate_text(issues: list) -> str:
    if not issues:
        return "OK: no issues\n"
    lines = []
    for i in issues:
        loc = f"L{i.line} " if i.line is not None else ""
        lines.append(f"{i.severity.upper()} {loc}{i.code}: {i.message}")
    return "\n".join(lines) + "\n"


def _parse_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_optional_bool(value: str | bool | None) -> bool | None:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_extract_zip(zf: zipfile.ZipFile, dest: Path) -> None:
    dest = dest.resolve()
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename
        if name.startswith("/") or ".." in Path(name).parts:
            _http_error(
                400,
                "Unsafe zip entry",
                f"rejected path '{name}'",
                "Re-pack the zip without absolute or parent paths",
            )
        target = (dest / name).resolve()
        if not str(target).startswith(str(dest)):
            _http_error(
                400,
                "Unsafe zip entry",
                f"rejected path '{name}'",
                "Re-pack the zip without path traversal",
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info) as src, target.open("wb") as out:
            shutil.copyfileobj(src, out)


def _batch_convert_sync(
    *,
    work_root: Path,
    source_dir: Path,
    preset: str,
    toc: bool | None,
    numbering: bool | None,
    toc_title: str | None,
    title: str | None,
    author: str | None,
    date: str | None,
    doc_version: str | None,
    page_numbers: bool,
    template_path: Path | None,
    figure_label: str | None,
    table_label: str | None,
    section_label: str | None,
    normalize: bool,
    no_plugins: bool,
    strict_mermaid: bool,
    exclude: tuple[str, ...],
    dry_run: bool,
    skip_existing: bool,
) -> tuple[bytes | None, dict[str, Any]]:
    source_dir = source_dir.resolve()
    md_files = collect_md_files(
        source_dir,
        exclude_patterns=exclude,
        apply_default_excludes=True,
    )
    if len(md_files) > MAX_BATCH_FILES:
        raise ValueError(
            f"too many markdown files ({len(md_files)}); max is {MAX_BATCH_FILES}"
        )
    if not md_files:
        raise ValueError("no .md files found after excludes")

    planned: list[str] = []
    skipped: list[str] = []
    out_dir = work_root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    options = _build_convert_options(
        preset=preset,
        toc=toc,
        numbering=numbering,
        toc_title=toc_title,
        title=title,
        author=author,
        date=date,
        doc_version=doc_version,
        page_numbers=page_numbers,
        template_path=template_path,
        figure_label=figure_label,
        table_label=table_label,
        section_label=section_label,
        normalize=normalize,
        no_plugins=no_plugins,
        strict_mermaid=strict_mermaid,
    )

    for md in md_files:
        rel = md.relative_to(source_dir)
        rel_docx = rel.with_suffix(".docx").as_posix()
        out_path = out_dir / rel.with_suffix(".docx")
        if skip_existing and out_path.is_file():
            skipped.append(rel_docx)
            continue
        planned.append(rel.as_posix())
        if dry_run:
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        convert_file(
            md,
            out_path,
            template_path=options.template,
            toc=bool(options.toc),
            toc_title=options.toc_title,
            numbering=options.numbering,
            title=options.title,
            author=options.author,
            date=options.date,
            doc_version=options.doc_version,
            page_numbers=options.page_numbers,
            figure_label=options.figure_label,
            table_label=options.table_label,
            section_label=options.section_label,
            normalize=options.normalize,
            strict_mermaid=options.strict_mermaid,
            no_plugins=no_plugins,
        )

    meta = {"planned": planned, "skipped": skipped, "count": len(planned)}
    if dry_run:
        return None, meta

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(out_dir.rglob("*.docx")):
            zf.write(path, path.relative_to(out_dir).as_posix())
    return buf.getvalue(), meta


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
    if body.format == "text":
        return PlainTextResponse(
            _format_validate_text(issues),
            media_type="text/plain; charset=utf-8",
        )
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


async def _run_convert(
    *,
    markdown: str,
    preset: str,
    toc: bool | None,
    numbering: bool | None,
    toc_title: str | None,
    title: str | None,
    author: str | None,
    date: str | None,
    doc_version: str | None,
    page_numbers: bool,
    template_key: str | None,
    template_bytes: bytes | None,
    template_name: str | None,
    figure_label: str | None,
    table_label: str | None,
    section_label: str | None,
    normalize: bool,
    no_plugins: bool,
    strict_mermaid: bool,
) -> FileResponse:
    if preset not in PLAYGROUND_PRESETS:
        _http_error(
            400,
            "Invalid preset",
            f"preset '{preset}' is not available in playground",
            f"Use one of: {', '.join(PLAYGROUND_PRESETS)}",
        )
    if not markdown.strip():
        _http_error(
            400,
            "Empty document",
            "markdown is empty",
            "Add content before generating DOCX",
        )

    template_path: Path | None = None
    tmp_template: Path | None = None
    if template_bytes:
        if not (template_name or "").lower().endswith(".docx"):
            _http_error(
                400,
                "Unsupported template",
                f"got '{template_name or ''}'",
                "Upload a .docx Word template",
            )
        tmp_dir = Path(tempfile.mkdtemp(prefix="md_to_docx_tpl_"))
        tmp_template = tmp_dir / "template.docx"
        tmp_template.write_bytes(template_bytes)
        template_path = tmp_template
    else:
        template_path = _resolve_community_template(template_key)

    try:
        out_path = await asyncio.wait_for(
            run_in_threadpool(
                _convert_sync,
                markdown,
                preset,
                toc,
                numbering,
                toc_title,
                title,
                author,
                date,
                doc_version,
                page_numbers,
                template_path,
                figure_label,
                table_label,
                section_label,
                normalize,
                no_plugins,
                strict_mermaid,
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
    finally:
        if tmp_template is not None:
            shutil.rmtree(tmp_template.parent, ignore_errors=True)

    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="document.docx",
        background=None,
    )


@app.post("/api/convert")
async def api_convert(request: Request):
    ctype = request.headers.get("content-type", "")
    if "multipart/form-data" in ctype:
        form = await request.form()
        markdown = str(form.get("markdown") or "")
        if len(markdown.encode("utf-8")) > MAX_BODY_BYTES:
            _http_error(
                413,
                "Request too large",
                f"markdown exceeds {MAX_BODY_BYTES} bytes",
                "Reduce markdown size below 400KB",
            )
        template_upload = form.get("template_file")
        template_bytes = None
        template_name = None
        if template_upload is not None and hasattr(template_upload, "read"):
            data = await template_upload.read()
            if len(data) > MAX_UPLOAD_BYTES:
                _http_error(
                    413,
                    "Request too large",
                    f"template exceeds {MAX_UPLOAD_BYTES} bytes",
                    "Use a smaller .docx template (max 2MB)",
                )
            if data:
                template_bytes = data
                template_name = getattr(template_upload, "filename", "template.docx")

        toc_raw = form.get("toc")
        numbering_raw = form.get("numbering")
        return await _run_convert(
            markdown=markdown,
            preset=str(form.get("preset") or "technical"),
            toc=_parse_optional_bool(toc_raw if isinstance(toc_raw, str) else None),
            numbering=_parse_optional_bool(
                numbering_raw if isinstance(numbering_raw, str) else None
            ),
            toc_title=str(form["toc_title"]) if form.get("toc_title") else None,
            title=str(form["title"]) if form.get("title") else None,
            author=str(form["author"]) if form.get("author") else None,
            date=str(form["date"]) if form.get("date") else None,
            doc_version=str(form["doc_version"]) if form.get("doc_version") else None,
            page_numbers=_parse_bool(form.get("page_numbers"), True),
            template_key=str(form["template"]) if form.get("template") else None,
            template_bytes=template_bytes,
            template_name=template_name,
            figure_label=str(form["figure_label"]) if form.get("figure_label") else None,
            table_label=str(form["table_label"]) if form.get("table_label") else None,
            section_label=str(form["section_label"]) if form.get("section_label") else None,
            normalize=_parse_bool(form.get("normalize"), True),
            no_plugins=_parse_bool(form.get("no_plugins"), False),
            strict_mermaid=_parse_bool(form.get("strict_mermaid"), False),
        )

    try:
        body = ConvertRequest.model_validate(await request.json())
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return await _run_convert(
        markdown=body.markdown,
        preset=body.preset,
        toc=body.toc,
        numbering=body.numbering,
        toc_title=body.toc_title,
        title=body.title,
        author=body.author,
        date=body.date,
        doc_version=body.doc_version,
        page_numbers=body.page_numbers,
        template_key=body.template,
        template_bytes=None,
        template_name=None,
        figure_label=body.figure_label,
        table_label=body.table_label,
        section_label=body.section_label,
        normalize=body.normalize,
        no_plugins=body.no_plugins,
        strict_mermaid=body.strict_mermaid,
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


@app.post("/api/convert/batch")
async def api_convert_batch(request: Request):
    form = await request.form()
    preset = str(form.get("preset") or "technical")
    if preset not in PLAYGROUND_PRESETS:
        _http_error(
            400,
            "Invalid preset",
            f"preset '{preset}' is not available in playground",
            f"Use one of: {', '.join(PLAYGROUND_PRESETS)}",
        )

    uploads: list[UploadFile] = []
    archive: UploadFile | None = None
    template_upload: UploadFile | None = None
    for key, value in form.multi_items():
        if not hasattr(value, "read"):
            continue
        if key == "archive":
            archive = value  # type: ignore[assignment]
        elif key == "template_file":
            template_upload = value  # type: ignore[assignment]
        elif key == "files":
            uploads.append(value)  # type: ignore[arg-type]

    file_list = [f for f in uploads if f.filename]
    has_archive = archive is not None and bool(archive.filename)
    if not file_list and not has_archive:
        _http_error(
            400,
            "No files",
            "upload at least one .md or a .zip archive",
            "Drag Markdown files or a zip into the batch panel",
        )
    if file_list and has_archive:
        _http_error(
            400,
            "Mixed upload",
            "provide either markdown files or a zip, not both",
            "Clear one input and try again",
        )

    exclude_raw = str(form.get("exclude") or "")
    exclude_patterns = tuple(
        line.strip()
        for line in exclude_raw.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )

    template_path: Path | None = None
    tmp_template_dir: Path | None = None
    if template_upload is not None and template_upload.filename:
        tpl_data = await _read_upload(template_upload, allowed=(".docx",))
        tmp_template_dir = Path(tempfile.mkdtemp(prefix="md_to_docx_btpl_"))
        template_path = tmp_template_dir / "template.docx"
        template_path.write_bytes(tpl_data)
    else:
        tpl_key = form.get("template")
        template_path = _resolve_community_template(
            str(tpl_key) if tpl_key else None
        )

    work = Path(tempfile.mkdtemp(prefix="md_to_docx_batch_"))
    source_dir = work / "src"
    source_dir.mkdir(parents=True, exist_ok=True)

    try:
        total = 0
        if has_archive:
            assert archive is not None
            data = await archive.read(MAX_BATCH_BYTES + 1)
            if len(data) > MAX_BATCH_BYTES:
                _http_error(
                    413,
                    "Request too large",
                    f"zip exceeds {MAX_BATCH_BYTES} bytes",
                    "Use a smaller archive (max 10MB)",
                )
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    _safe_extract_zip(zf, source_dir)
            except zipfile.BadZipFile as exc:
                _http_error(400, "Invalid zip", str(exc), "Upload a valid .zip file")
        else:
            for upload in file_list:
                name = upload.filename or "doc.md"
                if not name.lower().endswith(".md"):
                    _http_error(
                        400,
                        "Unsupported file",
                        f"got '{name}'",
                        "Only .md files are accepted for multi-file batch",
                    )
                chunk = await upload.read(MAX_BATCH_BYTES + 1)
                total += len(chunk)
                if total > MAX_BATCH_BYTES:
                    _http_error(
                        413,
                        "Request too large",
                        f"batch exceeds {MAX_BATCH_BYTES} bytes",
                        "Upload fewer or smaller files (max 10MB total)",
                    )
                safe_name = Path(name).name
                (source_dir / safe_name).write_bytes(chunk)

        toc = form.get("toc")
        numbering = form.get("numbering")

        def _run() -> tuple[bytes | None, dict[str, Any]]:
            return _batch_convert_sync(
                work_root=work,
                source_dir=source_dir,
                preset=preset,
                toc=_parse_optional_bool(str(toc) if toc is not None else None),
                numbering=_parse_optional_bool(
                    str(numbering) if numbering is not None else None
                ),
                toc_title=str(form["toc_title"]) if form.get("toc_title") else None,
                title=str(form["title"]) if form.get("title") else None,
                author=str(form["author"]) if form.get("author") else None,
                date=str(form["date"]) if form.get("date") else None,
                doc_version=str(form["doc_version"]) if form.get("doc_version") else None,
                page_numbers=_parse_bool(form.get("page_numbers"), True),
                template_path=template_path,
                figure_label=str(form["figure_label"]) if form.get("figure_label") else None,
                table_label=str(form["table_label"]) if form.get("table_label") else None,
                section_label=str(form["section_label"])
                if form.get("section_label")
                else None,
                normalize=_parse_bool(form.get("normalize"), True),
                no_plugins=_parse_bool(form.get("no_plugins"), False),
                strict_mermaid=_parse_bool(form.get("strict_mermaid"), False),
                exclude=exclude_patterns,
                dry_run=_parse_bool(form.get("dry_run"), False),
                skip_existing=_parse_bool(form.get("skip_existing"), False),
            )

        try:
            zip_bytes, meta = await asyncio.wait_for(
                run_in_threadpool(_run),
                timeout=BATCH_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            _http_error(
                500,
                "Batch timed out",
                f"exceeded {BATCH_TIMEOUT_SEC}s",
                "Upload fewer files or simplify documents",
            )
        except ValueError as exc:
            _http_error(400, "Batch failed", str(exc), "Check files and exclude rules")
        except MdToDocxError as exc:
            raise HTTPException(status_code=400, detail=exc.to_dict())
        except Exception as exc:
            _http_error(
                500,
                "Batch failed",
                str(exc),
                "Check markdown files and try again",
            )

        if zip_bytes is None:
            return JSONResponse(meta)
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="documents.zip"',
                "X-Batch-Count": str(meta.get("count", 0)),
            },
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if tmp_template_dir is not None:
            shutil.rmtree(tmp_template_dir, ignore_errors=True)


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
