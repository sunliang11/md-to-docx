"""Examples smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from md_to_docx.converter import convert_file


@pytest.mark.parametrize("example_md", sorted(Path("examples").glob("*/example.md")))
def test_example_converts(example_md: Path, tmp_path: Path):
    out = tmp_path / f"{example_md.parent.name}.docx"
    convert_file(example_md, out)
    assert out.stat().st_size > 2000
