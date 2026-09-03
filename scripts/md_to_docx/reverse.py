"""Reverse conversion: DOCX → Markdown."""

from __future__ import annotations

from pathlib import Path

from md_to_docx.parse.docx import parse_docx
from md_to_docx.write.markdown import write_markdown


def reverse_docx(
    docx_path: Path,
    out_path: Path,
    *,
    engine: str = "native",
) -> None:
    """Convert DOCX to Markdown."""
    if engine != "native":
        raise RuntimeError(f"unknown reverse engine: {engine} (only native is supported)")

    doc = parse_docx(docx_path)
    md = write_markdown(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
