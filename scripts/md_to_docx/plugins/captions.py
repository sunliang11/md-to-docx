"""Captions plugin — assigns figure/table numbers."""

from __future__ import annotations

from md_to_docx.ast import nodes as n
from md_to_docx.plugin.base import PluginBase, PluginContext


class CaptionsPlugin(PluginBase):
    name = "captions"

    def transform(self, document: n.Document, ctx: PluginContext) -> n.Document:
        fig_num = 0
        tbl_num = 0
        new_blocks: list[n.Block] = []
        ctx.config["xref_map"] = {}

        for block in document.blocks:
            if isinstance(block, n.Image) and (block.alt or block.title):
                fig_num += 1
                ident = block.identifier or f"fig-{fig_num}"
                caption = block.alt or block.title or ""
                fig = n.Figure(
                    image=block,
                    caption=caption,
                    identifier=ident.replace("fig:", ""),
                    number=fig_num,
                )
                ctx.config["xref_map"][f"fig:{fig.identifier or ident}"] = (
                    ctx.figure_label,
                    fig_num,
                )
                new_blocks.append(fig)
            elif isinstance(block, n.Table) and block.caption:
                tbl_num += 1
                ident = block.identifier or f"tbl-{tbl_num}"
                ctx.config["xref_map"][f"tbl:{ident.replace('tbl:', '')}"] = (
                    ctx.table_label,
                    tbl_num,
                )
                new_blocks.append(block)
            else:
                new_blocks.append(block)

        return n.Document(
            blocks=tuple(new_blocks),
            metadata=document.metadata,
            footnotes=document.footnotes,
        )
