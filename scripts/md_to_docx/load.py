"""Load documents to AST from .md or .docx paths."""

from __future__ import annotations

from pathlib import Path

from md_to_docx.ast import nodes as n
from md_to_docx.parse.docx import parse_docx
from md_to_docx.parse.markdown import parse_markdown


def load_document(path: Path) -> n.Document:
    """Load a .md or .docx file into a Document AST."""
    suffix = path.suffix.lower()
    if suffix == ".md":
        text = path.read_text(encoding="utf-8")
        return parse_markdown(text, source_path=path)
    if suffix == ".docx":
        return parse_docx(path)
    raise ValueError(f"unsupported file type: {suffix}")
