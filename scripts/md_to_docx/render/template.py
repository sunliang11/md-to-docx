"""Load DOCX templates."""

from __future__ import annotations

from docx import Document
from docx.oxml.ns import qn
from pathlib import Path

from md_to_docx.paths import native_reference_doc


def clear_body(doc: Document) -> None:
    body = doc.element.body
    children = list(body)
    for child in children:
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def open_document(template_path: Path | None) -> Document:
    path = template_path or native_reference_doc()
    doc = Document(str(path))
    clear_body(doc)
    return doc
