"""Markdown parser tests."""

from md_to_docx.ast import nodes as n
from md_to_docx.parse.markdown import parse_markdown


def test_h1():
    doc = parse_markdown("# H1\n")
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], n.Heading)
    assert doc.blocks[0].level == 1


def test_paragraph_bold_code():
    doc = parse_markdown("**bold** and `code`\n")
    p = doc.blocks[0]
    assert isinstance(p, n.Paragraph)


def test_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    doc = parse_markdown(md)
    assert isinstance(doc.blocks[0], n.Table)
    assert len(doc.blocks[0].rows) == 2


def test_code_fence():
    doc = parse_markdown("```python\nx=1\n```\n")
    assert isinstance(doc.blocks[0], n.CodeBlock)
    assert doc.blocks[0].lang == "python"


def test_blockquote():
    doc = parse_markdown("> quote\n")
    assert isinstance(doc.blocks[0], n.BlockQuote)


def test_pagebreak():
    doc = parse_markdown("<!-- pagebreak -->\n")
    assert isinstance(doc.blocks[0], n.PageBreak)


def test_task_list():
    doc = parse_markdown("- [x] done\n- [ ] todo\n")
    assert isinstance(doc.blocks[0], n.ListBlock)


def test_chinese():
    doc = parse_markdown("# 中文标题\n\n段落。\n")
    assert isinstance(doc.blocks[0], n.Heading)


def test_mermaid_node():
    doc = parse_markdown("```mermaid\nflowchart LR\n  A-->B\n```\n")
    assert isinstance(doc.blocks[0], n.Mermaid)


def test_empty():
    doc = parse_markdown("")
    assert doc.blocks == ()
