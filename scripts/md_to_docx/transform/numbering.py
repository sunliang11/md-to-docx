"""Heading number prefix transformer."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


def apply_heading_numbers(document: n.Document, *, enabled: bool) -> n.Document:
    if not enabled:
        return document
    counters = [0, 0, 0, 0, 0, 0]

    def number_block(block: n.Block) -> n.Block:
        if isinstance(block, n.Heading):
            level = block.level
            counters[level - 1] += 1
            for i in range(level, 6):
                counters[i] = 0
            prefix = ".".join(str(counters[i]) for i in range(level) if counters[i] > 0) + " "
            return n.Heading(
                level=level,
                children=(n.Text(prefix),) + block.children,
                anchor=block.anchor,
            )
        if isinstance(block, n.ListBlock):
            return n.ListBlock(
                ordered=block.ordered,
                items=tuple(
                    n.ListItem(tuple(number_block(b) for b in item.children), item.checked)
                    for item in block.items
                ),
                start=block.start,
                tight=block.tight,
            )
        if isinstance(block, n.BlockQuote):
            return n.BlockQuote(tuple(number_block(b) for b in block.children))
        return block

    return n.Document(
        blocks=tuple(number_block(b) for b in document.blocks),
        metadata=document.metadata,
        footnotes=document.footnotes,
    )
