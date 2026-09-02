"""Frontmatter parser tests."""

from md_to_docx.parse.frontmatter import parse_frontmatter


def test_no_frontmatter():
    meta, body = parse_frontmatter("# Hello\n")
    assert meta.title is None
    assert body.startswith("# Hello")


def test_simple_frontmatter():
    text = "---\ntitle: My Doc\nauthor: Alice\n---\n# Body\n"
    meta, body = parse_frontmatter(text)
    assert meta.title == "My Doc"
    assert meta.author == "Alice"
    assert body.startswith("# Body")


def test_toc_bool():
    text = "---\ntoc: true\n---\n# X\n"
    meta, _ = parse_frontmatter(text)
    assert meta.toc is True
