"""API layer tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from md_to_docx.api import convert, validate_markdown
from md_to_docx.errors import MdToDocxError
from md_to_docx.mcp.paths import validate_output_path


def test_convert_markdown_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
  monkeypatch.setenv("MD_TO_DOCX_OUT", str(tmp_path))
  result = convert(
    markdown_text="# Hello\n\nWorld.",
    preset="professional",
  )
  assert result.output_path.is_file()
  assert result.output_path.stat().st_size > 500
  assert result.engine == "native"


def test_convert_preset_technical(tmp_path: Path):
  src = Path(__file__).parent / "fixtures" / "sample.md"
  dst = tmp_path / "sample.md"
  shutil.copy(src, dst)
  out = tmp_path / "sample.docx"
  result = convert(source=dst, output=out, preset="technical")
  assert result.output_path == out
  assert out.stat().st_size > 500


def test_path_jail_rejects(tmp_path: Path):
  input_file = tmp_path / "doc.md"
  input_file.write_text("# Hi", encoding="utf-8")
  with pytest.raises(MdToDocxError, match="Output path not allowed"):
    validate_output_path(Path("/etc/passenger.docx"), input_path=input_file)


def test_path_jail_allows_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
  monkeypatch.chdir(tmp_path)
  out = tmp_path / "out.docx"
  assert validate_output_path(out) == out.resolve()


def test_path_jail_allows_input_parent(tmp_path: Path):
  sub = tmp_path / "sub"
  sub.mkdir()
  md = sub / "a.md"
  md.write_text("# x", encoding="utf-8")
  out = sub / "a.docx"
  assert validate_output_path(out, input_path=md) == out.resolve()


def test_missing_template_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MD_TO_DOCX_OUT", str(tmp_path))

    def _missing(_preset):
        raise FileNotFoundError("template not found: /fake/missing.docx")

    monkeypatch.setattr("md_to_docx.api.preset_template_path", _missing)

    with pytest.raises(MdToDocxError) as exc_info:
        convert(markdown_text="# Test", preset="technical")
    assert "fix:" in str(exc_info.value)


def test_validate_markdown_empty():
  issues = validate_markdown("")
  assert any(i.code == "empty_document" for i in issues)
