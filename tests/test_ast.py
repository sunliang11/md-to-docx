"""AST node tests."""

from __future__ import annotations

import pytest

from md_to_docx.ast import nodes as n
from md_to_docx.ast.visitor import TextCollector


def test_document_equality():
    doc1 = n.Document(
        blocks=(
            n.Heading(1, (n.Text("Title"),)),
            n.Paragraph((n.Text("body"),)),
        )
    )
    doc2 = n.Document(
        blocks=(
            n.Heading(1, (n.Text("Title"),)),
            n.Paragraph((n.Text("body"),)),
        )
    )
    assert doc1 == doc2


def test_frozen_raises():
    doc = n.Document(blocks=())
    with pytest.raises(AttributeError):
        doc.blocks = ()  # type: ignore[misc]


def test_visitor_collects_text():
    doc = n.Document(
        blocks=(
            n.Paragraph((n.Text("hello "), n.Strong((n.Text("world"),)))),
        )
    )
    collector = TextCollector()
    for block in doc.blocks:
        collector.visit(block)
    assert collector.texts == ["hello ", "world"]


def test_invalid_heading_level():
    with pytest.raises(ValueError):
        n.Heading(7, (n.Text("bad"),))
