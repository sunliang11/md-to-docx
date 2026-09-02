"""Footnote rendering via OOXML."""

from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

_footnote_counter = 0


def add_footnote_ref(paragraph: Paragraph, key: str) -> None:
    global _footnote_counter  # noqa: PLW0603
    _footnote_counter += 1
    run = paragraph.add_run(f"[^{key}]")
    run.font.superscript = True


def ensure_footnotes_part(doc) -> None:
    """Placeholder for footnotes.xml part; full OOXML in future iterations."""
    return None
