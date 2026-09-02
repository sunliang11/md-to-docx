"""Caption numbering — re-export from plugin."""

from pathlib import Path

from md_to_docx.plugins.captions import CaptionsPlugin

__all__ = ["CaptionsPlugin", "assign_caption_numbers"]


def assign_caption_numbers(document, *, figure_label="Figure"):
    from md_to_docx.plugin.base import PluginContext

    plugin = CaptionsPlugin()
    ctx = PluginContext(base_dir=Path.cwd(), figure_label=figure_label)
    doc = plugin.transform(document, ctx)
    return doc, ctx.config.get("xref_map", {})
