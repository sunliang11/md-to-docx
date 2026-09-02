"""Experimental AST → HTML renderer for previews.

Not exposed via CLI. Future Playground preview may use this module
instead of client-side Markdown rendering.
"""

from __future__ import annotations

import html

from md_to_docx.ast import nodes as n

CALLOUT_CSS = """
.callout { border-left: 4px solid #6B7280; padding: 0.5em 1em; margin: 1em 0; }
.callout-warning { border-color: #F59E0B; background: #FFFBEB; }
.callout-info { border-color: #3B82F6; background: #EFF6FF; }
.callout-note { border-color: #6B7280; background: #F9FAFB; }
hr.pagebreak { border: none; border-top: 2px dashed #ccc; margin: 2em 0; }
"""


def _inline_html(children: tuple[n.Inline, ...]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, n.Text):
            parts.append(html.escape(child.value))
        elif isinstance(child, n.Strong):
            parts.append(f"<strong>{_inline_html(child.children)}</strong>")
        elif isinstance(child, n.Emphasis):
            parts.append(f"<em>{_inline_html(child.children)}</em>")
        elif isinstance(child, n.Strike):
            parts.append(f"<del>{_inline_html(child.children)}</del>")
        elif isinstance(child, n.Code):
            parts.append(f"<code>{html.escape(child.value)}</code>")
        elif isinstance(child, n.Link):
            text = _inline_html(child.children) or html.escape(child.href)
            parts.append(f'<a href="{html.escape(child.href)}">{text}</a>')
        elif isinstance(child, n.InlineImage):
            alt = html.escape(child.alt or "")
            parts.append(f'<img src="{html.escape(child.src)}" alt="{alt}">')
        elif isinstance(child, n.Break):
            parts.append("<br>")
        elif isinstance(child, n.SoftBreak):
            parts.append(" ")
        elif isinstance(child, n.MathInline):
            parts.append(f"<span class=\"math\">${html.escape(child.latex)}$</span>")
        elif isinstance(child, n.FootnoteRef):
            parts.append(f'<sup><a href="#fn-{html.escape(child.key)}">[{html.escape(child.key)}]</a></sup>')
        elif isinstance(child, n.CrossRef):
            parts.append(f'<a href="#{child.kind}-{html.escape(child.identifier)}">[@{child.kind}:{child.identifier}]</a>')
    return "".join(parts)


def _block_html(block: n.Block, lines: list[str]) -> None:
    if isinstance(block, n.Heading):
        tag = f"h{block.level}"
        text = _inline_html(block.children)
        anchor = f' id="{html.escape(block.anchor)}"' if block.anchor else ""
        lines.append(f"<{tag}{anchor}>{text}</{tag}>")
    elif isinstance(block, n.Paragraph):
        text = _inline_html(block.children)
        if text:
            lines.append(f"<p>{text}</p>")
    elif isinstance(block, n.ListBlock):
        tag = "ol" if block.ordered else "ul"
        lines.append(f"<{tag}>")
        for item in block.items:
            lines.append("<li>")
            for sub in item.children:
                if isinstance(sub, n.Paragraph):
                    lines.append(_inline_html(sub.children))
                else:
                    _block_html(sub, lines)
            lines.append("</li>")
        lines.append(f"</{tag}>")
    elif isinstance(block, n.Table):
        lines.append("<table>")
        for ri, row in enumerate(block.rows):
            lines.append("<tr>")
            cell_tag = "th" if ri == 0 and all(c.header for c in row) else "td"
            for cell in row:
                tag = "th" if cell.header else "td"
                cell_text = " ".join(
                    _inline_html(b.children) if isinstance(b, n.Paragraph) else ""
                    for b in cell.children
                )
                lines.append(f"<{tag}>{cell_text}</{tag}>")
            lines.append("</tr>")
        lines.append("</table>")
        if block.caption:
            lines.append(f"<p class=\"caption\">{html.escape(block.caption)}</p>")
    elif isinstance(block, n.CodeBlock):
        lang = html.escape(block.lang or "")
        code = html.escape(block.text)
        lines.append(f'<pre><code class="language-{lang}">{code}</code></pre>')
    elif isinstance(block, n.Mermaid):
        code = html.escape(block.source)
        lines.append(f'<pre class="mermaid">{code}</pre>')
    elif isinstance(block, n.MathBlock):
        lines.append(f'<div class="math-block">$${html.escape(block.latex)}$$</div>')
    elif isinstance(block, n.BlockQuote):
        lines.append("<blockquote>")
        for sub in block.children:
            _block_html(sub, lines)
        lines.append("</blockquote>")
    elif isinstance(block, n.Callout):
        cls = f"callout callout-{block.kind}"
        lines.append(f'<div class="{cls}">')
        for sub in block.children:
            _block_html(sub, lines)
        lines.append("</div>")
    elif isinstance(block, n.ThematicBreak):
        lines.append("<hr>")
    elif isinstance(block, n.Image):
        alt = html.escape(block.alt or "")
        lines.append(f'<img src="{html.escape(block.src)}" alt="{alt}">')
    elif isinstance(block, n.Figure):
        if isinstance(block.image, n.Image):
            alt = html.escape(block.caption or block.image.alt)
            lines.append(f'<figure><img src="{html.escape(block.image.src)}" alt="{alt}">')
            lines.append(f"<figcaption>{html.escape(block.caption)}</figcaption></figure>")
        elif isinstance(block.image, n.Mermaid):
            lines.append(f'<figure><pre class="mermaid">{html.escape(block.image.source)}</pre>')
            lines.append(f"<figcaption>{html.escape(block.caption)}</figcaption></figure>")
    elif isinstance(block, n.PageBreak):
        lines.append('<hr class="pagebreak">')
    elif isinstance(block, n.TableOfContents):
        lines.append(f"<nav class=\"toc\"><h2>{html.escape(block.title)}</h2></nav>")
    elif isinstance(block, n.HTMLBlock):
        lines.append(f"<!-- raw: {html.escape(block.raw)} -->")


def render_html(document: n.Document, *, title: str | None = None) -> str:
    """Serialize a Document AST to a minimal HTML page."""
    page_title = title or document.metadata.title or "Document"
    body_lines: list[str] = []
    for block in document.blocks:
        _block_html(block, body_lines)
    body = "\n".join(body_lines)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        f"  <meta charset=\"utf-8\">\n"
        f"  <title>{html.escape(page_title)}</title>\n"
        f"  <style>{CALLOUT_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )
