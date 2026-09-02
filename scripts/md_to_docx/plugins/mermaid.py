"""Mermaid plugin — renders diagrams to PNG/SVG."""

from __future__ import annotations

import sys
from pathlib import Path

from md_to_docx.ast import nodes as n
from md_to_docx.plugin.base import PluginBase, PluginContext
from md_to_docx.util.mmdc import render_mermaid_to_files


class MermaidPlugin(PluginBase):
    name = "mermaid"

    def render_assets(
        self,
        document: n.Document,
        ctx: PluginContext,
    ) -> tuple[n.Document, dict[str, Path]]:
        media = ctx.base_dir / f"{ctx.base_dir.name}-media"
        if ctx.config.get("md_path"):
            md_path = Path(str(ctx.config["md_path"]))
            media = md_path.parent / f"{md_path.stem}-media"
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
                    if ctx.strict_mermaid:
                        raise RuntimeError(msg) from exc
                    print(f"warning: {msg}", file=sys.stderr)
                    new_blocks.append(n.CodeBlock(block.source, lang="mermaid"))
            else:
                new_blocks.append(block)

        return (
            n.Document(
                blocks=tuple(new_blocks),
                metadata=document.metadata,
                footnotes=document.footnotes,
            ),
            media_paths,
        )
