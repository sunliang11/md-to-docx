"""Tests for md_to_docx."""

from md_to_docx.converter import normalize_md


def test_normalize_adds_blank_before_heading():
    text = "intro\n## Section\n"
    result = normalize_md(text)
    assert "\n\n## Section" in result


def test_normalize_preserves_table_rows():
    text = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    result = normalize_md(text)
    assert "| A | B |" in result
    assert "| 1 | 2 |" in result
    # No blank line injected between table rows
    lines = [ln for ln in result.split("\n") if ln.strip()]
    assert lines == ["| A | B |", "|---|---|", "| 1 | 2 |"]


def test_normalize_compresses_excessive_blank_lines():
    text = "a\n\n\n\n\nb\n"
    result = normalize_md(text)
    # 3+ consecutive blank lines are compressed to at most 2
    assert "\n\n\n\n" not in result
    assert "a\n\n\nb" in result


def test_normalize_trailing_newline_preserved():
    text = "# Title\n"
    assert normalize_md(text).endswith("\n")
