"""Uppercase all heading text — example third-party plugin."""

from __future__ import annotations

from md_to_docx.ast import nodes as n
from md_to_docx.plugin.base import PluginBase


def _uppercase_inlines(children: tuple[n.Inline, ...]) -> tuple[n.Inline, ...]:
    result: list[n.Inline] = []
    for child in children:
        if isinstance(child, n.Text):
            result.append(n.Text(child.value.upper()))
        elif isinstance(child, (n.Strong, n.Emphasis, n.Strike)):
            inner = _uppercase_inlines(child.children)
            result.append(type(child)(inner))
        else:
            result.append(child)
    return tuple(result)


class UppercaseHeadingsPlugin(PluginBase):
    name = "uppercase_headings"

    def transform(self, document: n.Document, ctx) -> n.Document:
        new_blocks: list[n.Block] = []
        for block in document.blocks:
            if isinstance(block, n.Heading):
                new_blocks.append(
                    n.Heading(block.level, _uppercase_inlines(block.children), block.anchor)
                )
            else:
                new_blocks.append(block)
        return n.Document(
            blocks=tuple(new_blocks),
            metadata=document.metadata,
            footnotes=document.footnotes,
        )


plugin = UppercaseHeadingsPlugin()
