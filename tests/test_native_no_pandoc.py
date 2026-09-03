"""Native conversion works without pandoc on PATH."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest import mock

from md_to_docx.converter import convert_file


def test_native_without_pandoc(tmp_path: Path):
    src = Path("tests/fixtures/sample.md")
    dst = tmp_path / "sample.md"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "sample.docx"
    with mock.patch.object(shutil, "which", return_value=None):
        convert_file(dst, out, engine="native")
    assert out.is_file() and out.stat().st_size > 0
