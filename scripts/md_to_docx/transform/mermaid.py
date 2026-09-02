"""Mermaid diagram transformer — re-export from plugin."""

from md_to_docx.plugins.mermaid import MermaidPlugin

__all__ = ["MermaidPlugin", "transform_mermaid", "media_dir_for"]


def media_dir_for(md_path):
    from pathlib import Path

    return Path(md_path).parent / f"{Path(md_path).stem}-media"


def transform_mermaid(document, *, md_path, strict=False):
    from md_to_docx.plugin.base import PluginContext

    plugin = MermaidPlugin()
    ctx = PluginContext(
        base_dir=md_path.parent,
        config={"md_path": str(md_path)},
        strict_mermaid=strict,
    )
    return plugin.render_assets(document, ctx)
