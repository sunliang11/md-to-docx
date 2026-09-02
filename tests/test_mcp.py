"""MCP handler tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from md_to_docx.mcp.handlers import (
    handle_convert_markdown,
    handle_list_presets,
    handle_validate_document,
)


def test_list_presets():
    result = handle_list_presets({})
    assert result["ok"] is True
    names = {p["name"] for p in result["presets"]}
    assert "technical" in names
    assert "editorial" in names
    assert "wecom" in names


def test_convert_markdown_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MD_TO_DOCX_OUT", str(tmp_path))
    out = tmp_path / "out.docx"
    result = handle_convert_markdown(
        {
            "markdown": "# Title\n\nBody.",
            "output_path": str(out),
            "preset": "professional",
        }
    )
    assert result["ok"] is True
    assert Path(result["output_path"]).is_file()


def test_convert_input_path(tmp_path: Path):
    src = Path(__file__).parent / "fixtures" / "sample.md"
    dst = tmp_path / "sample.md"
    shutil.copy(src, dst)
    out = tmp_path / "sample.docx"
    result = handle_convert_markdown(
        {
            "input_path": str(dst),
            "output_path": str(out),
            "preset": "technical",
        }
    )
    assert result["ok"] is True
    assert out.stat().st_size > 500


def test_validate_document_markdown():
    result = handle_validate_document({"markdown": "# Hi"})
    assert result["ok"] is True
    assert isinstance(result["issues"], list)


def test_validate_empty_markdown():
    result = handle_validate_document({"markdown": ""})
    assert result["ok"] is True
    codes = [i["code"] for i in result["issues"]]
    assert "empty_document" in codes


def test_path_jail_in_convert(tmp_path: Path):
    src = tmp_path / "a.md"
    src.write_text("# x", encoding="utf-8")
    result = handle_convert_markdown(
        {
            "input_path": str(src),
            "output_path": "/etc/evil.docx",
        }
    )
    assert result["ok"] is False
    assert "problem" in result
