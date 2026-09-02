"""Native engine works without pandoc."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

from md_to_docx.converter import convert_file


def test_native_without_pandoc(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "sample.md"
    dst = tmp_path / "sample.md"
    shutil.copy(src, dst)
    out = tmp_path / "sample.docx"
    with patch("shutil.which", return_value=None):
        convert_file(dst, out, engine="native")
    assert out.is_file()
    assert out.stat().st_size > 1000
