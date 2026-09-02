"""Tests for AST → Markdown writer."""

from __future__ import annotations

from pathlib import Path

from md_to_docx.ast import nodes as n
from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.write.markdown import write_markdown


def _block_types(doc: n.Document) -> list[str]:
    return [type(b).__name__ for b in doc.blocks]


def test_write_markdown_roundtrip_block_types() -> None:
    src = Path("tests/fixtures/sample.md").read_text(encoding="utf-8")
    original = parse_markdown(src)
    md = write_markdown(original)
    roundtrip = parse_markdown(md)
    assert _block_types(original) == _block_types(roundtrip)
