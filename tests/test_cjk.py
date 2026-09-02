"""CJK output tests."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from md_to_docx.converter import convert_file


def test_cjk_text_in_docx(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "cjk.md"
    dst = tmp_path / "cjk.md"
    shutil.copy(src, dst)
    out = tmp_path / "cjk.docx"
    convert_file(dst, out, engine="native")
    with zipfile.ZipFile(out) as zf:
        xml = zf.read("word/document.xml").decode()
        styles = zf.read("word/styles.xml").decode()
    assert "中文标题" in xml
    assert "Microsoft YaHei" in styles or "eastAsia" in styles
