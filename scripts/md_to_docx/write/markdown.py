"""Document AST → Markdown writer."""

from __future__ import annotations

from md_to_docx.ast import nodes as n


def _inline_text(children: tuple[n.Inline, ...]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, n.Text):
            parts.append(child.value)
        elif isinstance(child, n.Strong):
            parts.append(f"**{_inline_text(child.children)}**")
        elif isinstance(child, n.Emphasis):
            parts.append(f"*{_inline_text(child.children)}*")
        elif isinstance(child, n.Strike):
            parts.append(f"~~{_inline_text(child.children)}~~")
        elif isinstance(child, n.Code):
            parts.append(f"`{child.value}`")
        elif isinstance(child, n.Link):
            text = _inline_text(child.children) or child.href
            parts.append(f"[{text}]({child.href})")
        elif isinstance(child, n.InlineImage):
            alt = child.alt or ""
            parts.append(f"![{alt}]({child.src})")
        elif isinstance(child, n.Break):
            parts.append("  \n")
        elif isinstance(child, n.SoftBreak):
            parts.append(" ")
        elif isinstance(child, n.MathInline):
            parts.append(f"${child.latex}$")
        elif isinstance(child, n.FootnoteRef):
            parts.append(f"[^{child.key}]")
        elif isinstance(child, n.CrossRef):
            parts.append(f"[@{child.kind}:{child.identifier}]")
    return "".join(parts)


def _write_inlines(children: tuple[n.Inline, ...]) -> str:
    return _inline_text(children)


def _write_block(block: n.Block, lines: list[str]) -> None:
    if isinstance(block, n.Heading):
        prefix = "#" * block.level
        text = _write_inlines(block.children)
        if block.anchor:
            lines.append(f"{prefix} {text} {{#{block.anchor}}}")
        else:
            lines.append(f"{prefix} {text}")
        lines.append("")
    elif isinstance(block, n.Paragraph):
        text = _write_inlines(block.children)
        if text:
            lines.append(text)
            lines.append("")
    elif isinstance(block, n.ListBlock):
        for i, item in enumerate(block.items):
            marker = f"{block.start + i}." if block.ordered else "-"
            for sub in item.children:
                if isinstance(sub, n.Paragraph):
                    text = _write_inlines(sub.children)
                    lines.append(f"{marker} {text}")
                else:
                    _write_block(sub, lines)
        lines.append("")
    elif isinstance(block, n.Table):
        if block.rows:
            for ri, row in enumerate(block.rows):
                cells: list[str] = []
                for cell in row:
                    cell_text = " ".join(
                        _write_inlines(b.children)
                        if isinstance(b, n.Paragraph)
                        else ""
                        for b in cell.children
                    ).strip()
                    cells.append(cell_text.replace("|", "\\|"))
                lines.append("| " + " | ".join(cells) + " |")
                if ri == 0:
                    lines.append("| " + " | ".join("---" for _ in cells) + " |")
            if block.caption:
                ident = block.identifier or "tbl"
                lines.append(f"Table: {block.caption} {{#tbl:{ident}}}")
            lines.append("")
    elif isinstance(block, n.CodeBlock):
        lang = block.lang or ""
        lines.append(f"```{lang}")
        lines.append(block.text.rstrip("\n"))
        lines.append("```")
        lines.append("")
    elif isinstance(block, n.Mermaid):
        lines.append("```mermaid")
        lines.append(block.source.rstrip("\n"))
        lines.append("```")
        lines.append("")
    elif isinstance(block, n.MathBlock):
        lines.append(f"$${block.latex}$$")
        lines.append("")
    elif isinstance(block, n.BlockQuote):
        for sub in block.children:
            if isinstance(sub, n.Paragraph):
                text = _write_inlines(sub.children)
                lines.append(f"> {text}")
            else:
                _write_block(sub, lines)
        lines.append("")
    elif isinstance(block, n.Callout):
        inner_lines: list[str] = []
        for sub in block.children:
            _write_block(sub, inner_lines)
        while inner_lines and inner_lines[-1] == "":
            inner_lines.pop()
        lines.append(f":::{block.kind}")
        lines.extend(inner_lines)
        lines.append(":::")
        lines.append("")
    elif isinstance(block, n.ThematicBreak):
        lines.append("---")
        lines.append("")
    elif isinstance(block, n.Image):
        alt = block.alt or ""
        suffix = ""
        if block.identifier:
            suffix = f" {{#fig:{block.identifier}}}"
        lines.append(f"![{alt}]({block.src}){suffix}")
        lines.append("")
    elif isinstance(block, n.Figure):
        if isinstance(block.image, n.Image):
            alt = block.caption or block.image.alt
            lines.append(
                f"![{alt}]({block.image.src}) {{#fig:{block.identifier}}}"
            )
        elif isinstance(block.image, n.Mermaid):
            lines.append("```mermaid")
            lines.append(block.image.source.rstrip("\n"))
            lines.append("```")
            lines.append(f"Figure: {block.caption} {{#fig:{block.identifier}}}")
        lines.append("")
    elif isinstance(block, n.PageBreak):
        lines.append("<!-- pagebreak -->")
        lines.append("")
    elif isinstance(block, n.TableOfContents):
        lines.append(f"<!-- toc: {block.title} -->")
        lines.append("")
    elif isinstance(block, n.HTMLBlock):
        lines.append(block.raw)
        lines.append("")


def write_markdown(doc: n.Document) -> str:
    """Serialize a Document AST to Markdown."""
    lines: list[str] = []
    meta = doc.metadata
    if meta.title or meta.author or meta.date:
        lines.append("---")
        if meta.title:
            lines.append(f"title: {meta.title}")
        if meta.author:
            lines.append(f"author: {meta.author}")
        if meta.date:
            lines.append(f"date: {meta.date}")
        lines.append("---")
        lines.append("")

    for block in doc.blocks:
        _write_block(block, lines)

    if doc.footnotes:
        for fn in doc.footnotes:
            lines.append(f"[^{fn.key}]:")
            for sub in fn.children:
                if isinstance(sub, n.Paragraph):
                    lines.append(f"    {_write_inlines(sub.children)}")
            lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"
