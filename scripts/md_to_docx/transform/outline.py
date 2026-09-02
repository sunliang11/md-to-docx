"""TOC insertion transformer."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


def insert_toc(document: n.Document, *, levels: int = 3, title: str = "Contents") -> n.Document:
    toc = n.TableOfContents(levels=levels, title=title)
    return n.Document(
        blocks=(toc,) + document.blocks,
        metadata=document.metadata,
        footnotes=document.footnotes,
    )
