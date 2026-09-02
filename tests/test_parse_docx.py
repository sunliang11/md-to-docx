"""Tests for DOCX → AST parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from md_to_docx.ast import nodes as n
from md_to_docx.engine.native import NativeOptions, convert_native
from md_to_docx.parse.docx import parse_docx
from md_to_docx.paths import native_reference_doc


def _inline_text(children: tuple[n.Inline, ...]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, n.Text):
            parts.append(child.value)
        elif isinstance(child, (n.Strong, n.Emphasis, n.Code)):
            parts.append(_inline_text(child.children))
    return "".join(parts)


@pytest.fixture
def sample_docx(tmp_path: Path) -> Path:
    md = Path("tests/fixtures/sample.md")
    out = tmp_path / "sample.docx"
    convert_native(
        md,
        out,
        options=NativeOptions(template_path=native_reference_doc()),
    )
    return out


def test_parse_docx_headings(sample_docx: Path) -> None:
    doc = parse_docx(sample_docx)
    headings = [b for b in doc.blocks if isinstance(b, n.Heading)]
    texts = [_inline_text(h.children) for h in headings]
    assert "Sample" in texts
    assert "Heading Two" in texts


def test_parse_docx_table(sample_docx: Path) -> None:
    doc = parse_docx(sample_docx)
    tables = [b for b in doc.blocks if isinstance(b, n.Table)]
    assert len(tables) >= 1


def test_parse_docx_code_block(sample_docx: Path) -> None:
    doc = parse_docx(sample_docx)
    code_blocks = [b for b in doc.blocks if isinstance(b, n.CodeBlock)]
    assert len(code_blocks) >= 1
    assert 'print("hello")' in code_blocks[0].text.strip()
