"""Caption numbering transformer."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


def assign_caption_numbers(document: n.Document, *, figure_label: str = "Figure") -> tuple[n.Document, dict[str, tuple[str, int]]]:
    fig_num = 0
    tbl_num = 0
    xref_map: dict[str, tuple[str, int]] = {}
    new_blocks: list[n.Block] = []

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
            xref_map[f"fig:{fig.identifier or ident}"] = (figure_label, fig_num)
            new_blocks.append(fig)
        elif isinstance(block, n.Table) and block.caption:
            tbl_num += 1
            ident = block.identifier or f"tbl-{tbl_num}"
            xref_map[f"tbl:{ident.replace('tbl:', '')}"] = ("Table", tbl_num)
            new_blocks.append(block)
        else:
            new_blocks.append(block)

    return (
        n.Document(blocks=tuple(new_blocks), metadata=document.metadata, footnotes=document.footnotes),
        xref_map,
    )
