"""Math plugin — placeholder; math is handled at parse/render time."""

from __future__ import annotations

from md_to_docx.plugin.base import PluginBase


class MathPlugin(PluginBase):
    name = "math"
