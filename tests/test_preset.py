"""Preset CLI tests."""

from __future__ import annotations

import shutil
from pathlib import Path

from md_to_docx.preset import load_preset


def test_load_preset():
    p = load_preset("technical")
    assert p.toc is True


def test_load_preset_editorial():
    p = load_preset("editorial")
    assert p.toc is True
    assert p.numbering is False


def test_unknown_preset():
    import pytest

    with pytest.raises(ValueError, match="unknown preset"):
        load_preset("foo")


def test_preset_conversion(tmp_path: Path):
    from md_to_docx.converter import convert_file

    src = Path(__file__).parent / "fixtures" / "sample.md"
    dst = tmp_path / "sample.md"
    shutil.copy(src, dst)
    out = tmp_path / "sample.docx"
    preset = load_preset("professional")
    from md_to_docx.preset import preset_template_path

    convert_file(
        dst,
        out,
        template_path=preset_template_path(preset),
        toc=preset.toc,
    )
    assert out.stat().st_size > 1000
