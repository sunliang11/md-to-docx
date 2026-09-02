"""Tests for AST document diff."""

from __future__ import annotations

from md_to_docx.ast import nodes as n
from md_to_docx.diff.ast_diff import Change, diff_documents, format_diff


def test_diff_heading_change() -> None:
    doc_a = n.Document(
        blocks=(
            n.Heading(1, (n.Text("Title"),)),
            n.Heading(2, (n.Text("Section A"),)),
            n.Paragraph((n.Text("Body"),)),
        )
    )
    doc_b = n.Document(
        blocks=(
            n.Heading(1, (n.Text("Title"),)),
            n.Heading(2, (n.Text("Section B"),)),
            n.Paragraph((n.Text("Body"),)),
        )
    )
    changes = diff_documents(doc_a, doc_b)
    assert any(c.op == "replace" or c.op == "remove" or c.op == "add" for c in changes)
    text_out = format_diff(changes, fmt="text")
    assert "Section" in text_out


def test_diff_identical() -> None:
    doc = n.Document(blocks=(n.Paragraph((n.Text("Same"),)),))
    assert diff_documents(doc, doc) == []


def test_format_json() -> None:
    changes = [Change(op="add", path="blocks[0]", summary="+ Added paragraph: hello")]
    out = format_diff(changes, fmt="json")
    assert '"op": "add"' in out
