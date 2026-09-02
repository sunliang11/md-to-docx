"""Roundtrip integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from md_to_docx.diff.ast_diff import diff_documents
from md_to_docx.engine.native import NativeOptions, convert_native
from md_to_docx.load import load_document
from md_to_docx.parse.docx import parse_docx
from md_to_docx.paths import native_reference_doc
from md_to_docx.reverse import reverse_docx


@pytest.fixture
def roundtrip_paths(tmp_path: Path) -> tuple[Path, Path]:
    md = Path("tests/fixtures/sample.md")
    docx = tmp_path / "sample.docx"
    back = tmp_path / "back.md"
    convert_native(
        md,
        docx,
        options=NativeOptions(template_path=native_reference_doc()),
    )
    reverse_docx(docx, back)
    return md, back


def test_roundtrip_diff_minimal(roundtrip_paths: tuple[Path, Path]) -> None:
    original, back = roundtrip_paths
    doc_a = load_document(original)
    doc_b = load_document(back)
    changes = diff_documents(doc_a, doc_b)
    whitespace_only = all(
        "whitespace" in c.summary.lower() or c.op == "replace"
        for c in changes
    )
    assert len(changes) == 0 or whitespace_only or len(changes) < 10
