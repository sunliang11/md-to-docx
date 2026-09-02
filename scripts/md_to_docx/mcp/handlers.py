"""MCP tool handlers (pure functions, no stdio)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from md_to_docx.api import convert, validate_markdown, validate_path
from md_to_docx.errors import MdToDocxError, missing_input
from md_to_docx.mcp.paths import validate_output_path
from md_to_docx.preset import PRESETS

PRESET_DESCRIPTIONS: dict[str, str] = {
    "professional": "General documents with TOC",
    "editorial": "Editorial layout (Georgia/KaiTi, wide margins)",
    "technical": "Technical reports with TOC and heading numbering",
    "academic": "Academic papers (Times/SimSun)",
    "business": "Business summaries, no TOC",
    "report": "Meeting notes and reports",
    "wecom": "WeCom smart-doc import (requires pandoc)",
}


def _error_dict(exc: MdToDocxError) -> dict[str, Any]:
    return {"ok": False, **exc.to_dict()}


def handle_convert_markdown(args: dict[str, Any]) -> dict[str, Any]:
    input_path = args.get("input_path")
    markdown = args.get("markdown")
    if input_path is None and markdown is None:
        return _error_dict(missing_input())

    source: Path | None = None
    if input_path:
        source = Path(input_path).expanduser().resolve()
        if not source.is_file():
            return _error_dict(
                MdToDocxError(
                    "Input file not found",
                    f"no file at {source}",
                    "Provide a valid input_path or markdown text",
                )
            )

    output_path = args.get("output_path")
    output: Path | None = None
    if output_path:
        try:
            output = validate_output_path(
                Path(output_path),
                input_path=source,
            )
        except MdToDocxError as exc:
            return _error_dict(exc)

    template = args.get("template")
    template_path = Path(template).expanduser() if template else None

    try:
        result = convert(
            source=source,
            markdown_text=markdown,
            output=output,
            preset=args.get("preset"),
            template=template_path,
            engine=args.get("engine"),
            toc=args.get("toc"),
        )
    except MdToDocxError as exc:
        return _error_dict(exc)

    return {
        "ok": True,
        "output_path": str(result.output_path),
        "warnings": result.warnings,
        "engine": result.engine,
    }


def handle_apply_template(args: dict[str, Any]) -> dict[str, Any]:
    input_path = args.get("input_path")
    template = args.get("template")
    output_path = args.get("output_path")
    if not input_path or not template or not output_path:
        return _error_dict(
            MdToDocxError(
                "Missing arguments",
                "apply_template requires input_path, template, and output_path",
                "Provide all three fields",
            )
        )
    return handle_convert_markdown(
        {
            "input_path": input_path,
            "template": template,
            "output_path": output_path,
        }
    )


def handle_validate_document(args: dict[str, Any]) -> dict[str, Any]:
    input_path = args.get("input_path")
    markdown = args.get("markdown")
    strict = bool(args.get("strict", False))

    if input_path is None and markdown is None:
        return _error_dict(missing_input())

    try:
        if markdown is not None:
            issues = validate_markdown(markdown, strict=strict)
        else:
            path = Path(input_path).expanduser().resolve()
            if not path.is_file():
                return _error_dict(
                    MdToDocxError(
                        "Input file not found",
                        f"no file at {path}",
                        "Provide a valid input_path or markdown text",
                    )
                )
            issues = validate_path(path, strict=strict)
    except MdToDocxError as exc:
        return _error_dict(exc)

    return {
        "ok": True,
        "issues": [i.__dict__ for i in issues],
    }


def handle_list_presets(_args: dict[str, Any] | None = None) -> dict[str, Any]:
    presets = []
    for name, preset in sorted(PRESETS.items()):
        presets.append(
            {
                "name": name,
                "engine": preset.engine,
                "toc": preset.toc,
                "numbering": preset.numbering,
                "description": PRESET_DESCRIPTIONS.get(name, ""),
            }
        )
    return {"ok": True, "presets": presets}
