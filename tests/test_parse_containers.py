"""Pagebreak container parsing."""

from md_to_docx.ast import nodes as n
from md_to_docx.parse.markdown import parse_markdown


def test_html_pagebreak():
    doc = parse_markdown("<!-- pagebreak -->\n")
    assert isinstance(doc.blocks[0], n.PageBreak)


def test_container_pagebreak():
    doc = parse_markdown(":::pagebreak\n:::\n")
    assert any(isinstance(b, n.PageBreak) for b in doc.blocks)
