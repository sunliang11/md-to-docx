"""TOC field tests."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from md_to_docx.converter import convert_file


def test_toc_field_present(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "sample.md"
    dst = tmp_path / "sample.md"
    shutil.copy(src, dst)
    out = tmp_path / "out.docx"
    convert_file(dst, out, toc=True)
    with zipfile.ZipFile(out) as zf:
        xml = zf.read("word/document.xml").decode()
    assert "TOC" in xml
