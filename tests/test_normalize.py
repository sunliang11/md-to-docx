"""Tests for md_to_docx normalization."""

from md_to_docx.converter import normalize_md
from md_to_docx.normalizer import normalize_markdown_content


def test_normalize_adds_blank_before_heading():
    text = "intro\n## Section\n"
    result = normalize_md(text)
    assert "\n\n## Section" in result


def test_normalize_preserves_table_rows():
    text = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    result = normalize_md(text)
    lines = [ln for ln in result.split("\n") if ln.strip()]
    assert len(lines) == 3
    assert "---" in lines[1]
    assert "A" in lines[0] and "B" in lines[0]
    assert "1" in lines[2] and "2" in lines[2]


def test_normalize_compresses_excessive_blank_lines():
    text = "a\n\n\n\n\nb\n"
    result = normalize_md(text)
    assert "\n\n\n\n" not in result
    # Content normalization removes blank lines between plain paragraphs.
    assert result.strip() == "a\nb"


def test_normalize_trailing_newline_preserved():
    text = "# Title\n"
    assert normalize_md(text).endswith("\n")


def test_content_normalize_adds_table_separator():
    text = "| A | B |\n| 1 | 2 |\n"
    result = normalize_markdown_content(text)
    assert "|---|---|" in result


def test_content_normalize_aligns_table_columns():
    text = "| A | B | C |\n|---|---|\n| 1 | 2 |\n| a | b | c | d |\n"
    result = normalize_markdown_content(text)
    data_rows = [
        ln for ln in result.split("\n") if ln.startswith("|") and "---" not in ln
    ]
    col_counts = [ln.count("|") - 1 for ln in data_rows]
    assert len(set(col_counts)) == 1


def test_content_normalize_fixes_bullet_spacing():
    text = "-项目\n"
    result = normalize_markdown_content(text)
    assert "- 项目" in result


def test_content_normalize_converts_chinese_heading_number():
    text = "## 一、标题\n"
    result = normalize_markdown_content(text)
    assert "## 1. 标题" in result


def test_content_normalize_closes_unclosed_code_block():
    text = "```python\nprint('hi')\n"
    result = normalize_markdown_content(text)
    assert result.rstrip().endswith("```")


def test_content_normalize_removes_paragraph_leading_whitespace():
    text = "   段落文本\n"
    result = normalize_markdown_content(text)
    assert result.startswith("段落文本")


def test_content_normalize_horizontal_rule():
    text = "----\n"
    result = normalize_markdown_content(text)
    assert "---" in result


def test_content_normalize_unmatched_bold():
    text = "这是**只有开头\n"
    result = normalize_markdown_content(text)
    assert "**" not in result
