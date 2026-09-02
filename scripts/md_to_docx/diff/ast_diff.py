"""AST structured document diff."""

from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal

from md_to_docx.ast import nodes as n

ChangeOp = Literal["add", "remove", "replace"]


@dataclass(frozen=True, slots=True)
class Change:
    op: ChangeOp
    path: str
    summary: str


def _block_summary(block: n.Block) -> str:
    if isinstance(block, n.Heading):
        text = _inline_text(block.children)
        return f"heading: {text}"
    if isinstance(block, n.Paragraph):
        text = _inline_text(block.children)
        return f"paragraph: {text[:60]}" if text else "paragraph: (empty)"
    if isinstance(block, n.Table):
        return "table"
    if isinstance(block, n.CodeBlock):
        preview = block.text[:40].replace("\n", " ")
        return f"code: {preview}"
    if isinstance(block, n.ListBlock):
        kind = "ordered list" if block.ordered else "bullet list"
        return kind
    if isinstance(block, n.Image):
        return f"image: {block.src}"
    if isinstance(block, n.Figure):
        return f"figure: {block.caption}"
    if isinstance(block, n.Mermaid):
        return "mermaid diagram"
    if isinstance(block, n.MathBlock):
        return f"math: {block.latex[:40]}"
    if isinstance(block, n.BlockQuote):
        return "blockquote"
    if isinstance(block, n.Callout):
        return f"callout: {block.kind}"
    if isinstance(block, n.PageBreak):
        return "page break"
    if isinstance(block, n.ThematicBreak):
        return "thematic break"
    if isinstance(block, n.TableOfContents):
        return "table of contents"
    return type(block).__name__


def _inline_text(children: tuple[n.Inline, ...]) -> str:
    parts: list[str] = []
    for child in children:
        if isinstance(child, n.Text):
            parts.append(child.value)
        elif isinstance(child, (n.Strong, n.Emphasis, n.Strike, n.Code)):
            parts.append(_inline_text(child.children))
        elif isinstance(child, n.SoftBreak):
            parts.append(" ")
        elif isinstance(child, n.Break):
            parts.append("\n")
    return "".join(parts).strip()


def _blocks_equal(a: n.Block, b: n.Block) -> bool:
    if type(a) is not type(b):
        return False
    if isinstance(a, n.Heading) and isinstance(b, n.Heading):
        return a.level == b.level and _inline_text(a.children) == _inline_text(b.children)
    if isinstance(a, n.Paragraph) and isinstance(b, n.Paragraph):
        return _inline_text(a.children) == _inline_text(b.children)
    if isinstance(a, n.CodeBlock) and isinstance(b, n.CodeBlock):
        return a.text.strip() == b.text.strip() and a.lang == b.lang
    if isinstance(a, n.Table) and isinstance(b, n.Table):
        return len(a.rows) == len(b.rows)
    return repr(a) == repr(b)


def diff_documents(a: n.Document, b: n.Document) -> list[Change]:
    """Compare two documents at block level."""
    blocks_a = list(a.blocks)
    blocks_b = list(b.blocks)
    matcher = SequenceMatcher(
        None,
        [_block_summary(x) for x in blocks_a],
        [_block_summary(x) for x in blocks_b],
        autojunk=False,
    )
    changes: list[Change] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                if not _blocks_equal(blocks_a[i1 + k], blocks_b[j1 + k]):
                    changes.append(
                        Change(
                            op="replace",
                            path=f"blocks[{i1 + k}]",
                            summary=f"~ Modified {_block_summary(blocks_b[j1 + k])}",
                        )
                    )
        elif tag == "delete":
            for k in range(i1, i2):
                changes.append(
                    Change(
                        op="remove",
                        path=f"blocks[{k}]",
                        summary=f"- Removed {_block_summary(blocks_a[k])}",
                    )
                )
        elif tag == "insert":
            for k in range(j1, j2):
                changes.append(
                    Change(
                        op="add",
                        path=f"blocks[{k}]",
                        summary=f"+ Added {_block_summary(blocks_b[k])}",
                    )
                )
        elif tag == "replace":
            for k in range(i1, i2):
                changes.append(
                    Change(
                        op="remove",
                        path=f"blocks[{k}]",
                        summary=f"- Removed {_block_summary(blocks_a[k])}",
                    )
                )
            for k in range(j1, j2):
                changes.append(
                    Change(
                        op="add",
                        path=f"blocks[{k}]",
                        summary=f"+ Added {_block_summary(blocks_b[k])}",
                    )
                )
    return changes


def format_diff(changes: list[Change], fmt: str = "text") -> str:
    """Format diff changes for human or machine consumption."""
    if fmt == "json":
        return json.dumps(
            [{"op": c.op, "path": c.path, "summary": c.summary} for c in changes],
            indent=2,
        )
    if fmt == "md":
        lines = ["# Document changes", ""]
        for c in changes:
            lines.append(f"- {c.summary}")
        return "\n".join(lines) + "\n"
    return "\n".join(c.summary for c in changes) + ("\n" if changes else "")
