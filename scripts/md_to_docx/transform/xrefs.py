"""Cross-reference resolution."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


def resolve_xrefs(document: n.Document, xref_map: dict[str, tuple[str, int]]) -> n.Document:
    def resolve_inline(child: n.Inline) -> n.Inline:
        if isinstance(child, n.CrossRef):
            return child
        if isinstance(child, (n.Strong, n.Emphasis, n.Strike)):
            cls = type(child)
            return cls(tuple(resolve_inline(c) for c in child.children))
        if isinstance(child, n.Link):
            return n.Link(child.href, tuple(resolve_inline(c) for c in child.children), child.title)
        return child

    def resolve_block(block: n.Block) -> n.Block:
        if isinstance(block, n.Paragraph):
            return n.Paragraph(tuple(resolve_inline(c) for c in block.children))
        if isinstance(block, n.Heading):
            return n.Heading(block.level, tuple(resolve_inline(c) for c in block.children), block.anchor)
        return block

    return n.Document(
        blocks=tuple(resolve_block(b) for b in document.blocks),
        metadata=document.metadata,
        footnotes=document.footnotes,
    )
