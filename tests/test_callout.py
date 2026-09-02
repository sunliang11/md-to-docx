"""Callout container parsing and DOCX rendering."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from md_to_docx.ast import nodes as n
from md_to_docx.converter import convert_file
from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.write.markdown import write_markdown

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def test_parse_warning_callout():
    doc = parse_markdown(":::warning\nWatch out!\n:::\n")
    assert len(doc.blocks) == 1
    block = doc.blocks[0]
    assert isinstance(block, n.Callout)
    assert block.kind == "warning"
    assert len(block.children) == 1
    assert isinstance(block.children[0], n.Paragraph)


def test_parse_info_callout():
    doc = parse_markdown(":::info\nFor your information.\n:::\n")
    block = doc.blocks[0]
    assert isinstance(block, n.Callout)
    assert block.kind == "info"


def test_parse_note_callout():
    doc = parse_markdown(":::note\nA short note.\n:::\n")
    block = doc.blocks[0]
    assert isinstance(block, n.Callout)
    assert block.kind == "note"


def test_fixture_has_three_callouts():
    text = Path(__file__).parent.joinpath("fixtures", "callout.md").read_text()
    doc = parse_markdown(text)
    callouts = [b for b in doc.blocks if isinstance(b, n.Callout)]
    assert len(callouts) == 3
    assert {c.kind for c in callouts} == {"warning", "info", "note"}


def test_callout_roundtrip():
    original = ":::warning\nHello **world**.\n:::\n"
    doc = parse_markdown(original)
    restored = write_markdown(doc)
    doc2 = parse_markdown(restored)
    assert isinstance(doc2.blocks[0], n.Callout)
    assert doc2.blocks[0].kind == "warning"


def test_callout_docx_has_left_border(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "callout.md"
    dst = tmp_path / "callout.md"
    dst.write_text(src.read_text())
    out = tmp_path / "callout.docx"
    convert_file(dst, out, engine="native")
    assert out.is_file()

    with zipfile.ZipFile(out) as zf:
        with zf.open("word/document.xml") as f:
            root = etree.parse(f).getroot()
    borders = root.findall(".//w:pBdr/w:left", namespaces=NS)
    assert len(borders) >= 3
