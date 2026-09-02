"""Mermaid diagram transformer."""

from __future__ import annotations

import sys
from pathlib import Path

from md_to_docx.ast import nodes as n
from md_to_docx.util.mmdc import render_mermaid_to_files


def media_dir_for(md_path: Path) -> Path:
    return md_path.parent / f"{md_path.stem}-media"


def transform_mermaid(
    document: n.Document,
    *,
    md_path: Path,
    strict: bool = False,
) -> tuple[n.Document, dict[str, Path]]:
    media = media_dir_for(md_path)
    media.mkdir(parents=True, exist_ok=True)
    media_paths: dict[str, Path] = {}
    new_blocks: list[n.Block] = []
    idx = 0

    for block in document.blocks:
        if isinstance(block, n.Mermaid):
            idx += 1
            svg = media / f"mermaid_{idx:02d}.svg"
            png = media / f"mermaid_{idx:02d}.png"
            try:
                render_mermaid_to_files(block.source, svg, png=png)
                key = f"mermaid:{hash(block.source)}"
                media_paths[key] = png
                new_blocks.append(block)
            except Exception as exc:  # noqa: BLE001
                msg = f"mermaid render failed: {exc}"
                if strict:
                    raise RuntimeError(msg) from exc
                print(f"warning: {msg}", file=sys.stderr)
                new_blocks.append(n.CodeBlock(block.source, lang="mermaid"))
        else:
            new_blocks.append(block)

    return (
        n.Document(blocks=tuple(new_blocks), metadata=document.metadata, footnotes=document.footnotes),
        media_paths,
    )
