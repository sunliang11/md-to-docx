"""Validation tests."""

from pathlib import Path

from md_to_docx.validate import validate_file


def test_validate_comprehensive():
    path = Path(__file__).parent / "fixtures" / "comprehensive.md"
    issues = validate_file(path)
    assert isinstance(issues, list)


def test_validate_empty(tmp_path: Path):
    p = tmp_path / "empty.md"
    p.write_text("", encoding="utf-8")
    issues = validate_file(p)
    assert any(i.code == "empty_document" for i in issues)
