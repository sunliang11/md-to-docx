"""Experimental HTML renderer tests."""

from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.render.html import render_html


def test_render_heading():
    doc = parse_markdown("# Hello\n")
    html_out = render_html(doc)
    assert "<h1>Hello</h1>" in html_out


def test_render_callout():
    doc = parse_markdown(":::warning\nBe careful.\n:::\n")
    html_out = render_html(doc)
    assert 'class="callout callout-warning"' in html_out
    assert "Be careful." in html_out


def test_render_pagebreak():
    doc = parse_markdown("<!-- pagebreak -->\n")
    html_out = render_html(doc)
    assert 'class="pagebreak"' in html_out


def test_render_table():
    doc = parse_markdown("| A | B |\n|---|---|\n| 1 | 2 |\n")
    html_out = render_html(doc)
    assert "<table>" in html_out
    assert "<td>1</td>" in html_out
