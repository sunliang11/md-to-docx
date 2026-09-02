"""Built-in plugins."""

from __future__ import annotations

from md_to_docx.plugin.base import Plugin
from md_to_docx.plugins.captions import CaptionsPlugin
from md_to_docx.plugins.math import MathPlugin
from md_to_docx.plugins.mermaid import MermaidPlugin

BUILTIN_PLUGINS: list[type[Plugin]] = [
    MermaidPlugin,
    MathPlugin,
    CaptionsPlugin,
]
