"""Native engine DOCX output tests."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md_to_docx.converter import convert_file

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _xml(docx: Path, name: str):
    with zipfile.ZipFile(docx) as zf:
        with zf.open(name) as f:
            return etree.parse(f).getroot()


@pytest.fixture
def native_sample(tmp_path: Path) -> Path:
    src = Path(__file__).parent / "fixtures" / "sample.md"
    dst = tmp_path / "sample.md"
    shutil.copy(src, dst)
    out = tmp_path / "sample.docx"
    convert_file(dst, out)
    return out


def test_valid_docx(native_sample: Path):
    with zipfile.ZipFile(native_sample) as zf:
        assert "[Content_Types].xml" in zf.namelist()


def test_has_table(native_sample: Path):
    root = _xml(native_sample, "word/document.xml")
    assert root.findall(".//w:tbl", namespaces=NS)


def test_has_heading(native_sample: Path):
    root = _xml(native_sample, "word/document.xml")
    styles = [el.get(f"{{{NS['w']}}}val") for el in root.findall(".//w:pStyle", namespaces=NS)]
    assert any(s and "Heading" in s for s in styles)


def test_yahei_in_styles(native_sample: Path):
    root = _xml(native_sample, "word/styles.xml")
    east = [
        el.get(f"{{{NS['w']}}}eastAsia")
        for el in root.findall(".//w:rFonts", namespaces=NS)
    ]
    assert "Microsoft YaHei" in east


def _heading_color(docx: Path, style_id: str) -> str | None:
    root = _xml(docx, "word/styles.xml")
    for style in root.findall("w:style", namespaces=NS):
        if style.get(f"{{{NS['w']}}}styleId") != style_id:
            continue
        color = style.find(".//w:color", namespaces=NS)
        if color is None:
            return None
        return color.get(f"{{{NS['w']}}}val")
    return None


def test_heading_color_black(native_sample: Path):
    assert _heading_color(native_sample, "Heading1") == "000000"
    assert _heading_color(native_sample, "Heading2") == "000000"
