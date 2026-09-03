"""Tests for DOCX → AST parser."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md_to_docx.ast import nodes as n
from md_to_docx.engine.native import NativeOptions, convert_native
from md_to_docx.parse.docx import parse_docx
from md_to_docx.paths import native_reference_doc
from md_to_docx.reverse import reverse_docx

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

STYLES_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:style w:type="paragraph" w:styleId="00000e">
    <w:name w:val="标题 1"/>
    <w:pPr><w:outlineLvl w:val="0"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="000011">
    <w:name w:val="标题 2"/>
    <w:pPr><w:outlineLvl w:val="1"/></w:pPr>
  </w:style>
</w:styles>
"""

DOCUMENT_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="00000e"/></w:pPr>
      <w:r><w:t>Chapter One</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="000011"/></w:pPr>
      <w:r><w:t>Section A</w:t></w:r>
    </w:p>
  </w:body>
</w:document>
"""

BASED_ON_STYLES_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:style w:type="paragraph" w:styleId="00000e">
    <w:basedOn w:val="Heading1"/>
  </w:style>
</w:styles>
"""

BASED_ON_DOCUMENT_XML = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="00000e"/></w:pPr>
      <w:r><w:t>Chapter One</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="00000e"/></w:pPr>
    </w:p>
  </w:body>
</w:document>
"""


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


def _media_dir(docx: Path) -> Path:
    return docx.parent / f"{docx.stem}-media"


def test_convert_without_assets_skips_media_dir(sample_docx: Path) -> None:
    assert not _media_dir(sample_docx).exists()


def test_parse_without_assets_skips_media_dir(sample_docx: Path) -> None:
    parse_docx(sample_docx)
    assert not _media_dir(sample_docx).exists()


def test_reverse_without_assets_skips_media_dir(sample_docx: Path, tmp_path: Path) -> None:
    reverse_docx(sample_docx, tmp_path / "back.md")
    assert not _media_dir(sample_docx).exists()


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


def _write_custom_style_docx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/styles.xml", STYLES_XML)
        zf.writestr("word/document.xml", DOCUMENT_XML)


def test_parse_docx_custom_style_ids(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    docx = tmp_path / "custom-styles.docx"
    _write_custom_style_docx(docx)

    doc = parse_docx(docx)
    headings = [b for b in doc.blocks if isinstance(b, n.Heading)]
    assert len(headings) == 2
    assert headings[0].level == 1
    assert headings[1].level == 2
    assert _inline_text(headings[0].children) == "Chapter One"
    assert _inline_text(headings[1].children) == "Section A"
    assert "unhandled paragraph style" not in capsys.readouterr().err


def test_parse_docx_based_on_builtin_heading(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    docx = tmp_path / "based-on-builtin.docx"
    with zipfile.ZipFile(docx, "w") as zf:
        zf.writestr("word/styles.xml", BASED_ON_STYLES_XML)
        zf.writestr("word/document.xml", BASED_ON_DOCUMENT_XML)

    doc = parse_docx(docx)
    headings = [b for b in doc.blocks if isinstance(b, n.Heading)]
    assert len(headings) == 1
    assert headings[0].level == 1
    assert _inline_text(headings[0].children) == "Chapter One"
    assert "unhandled paragraph style" not in capsys.readouterr().err
