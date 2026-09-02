"""Plugin protocol and base class."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from md_to_docx.ast import nodes as n


@dataclass
class PluginContext:
    base_dir: Path
    config: dict[str, object] = field(default_factory=dict)
    strict_mermaid: bool = False
    figure_label: str = "Figure"
    table_label: str = "Table"


@runtime_checkable
class Plugin(Protocol):
    name: str

    def render_assets(
        self,
        document: n.Document,
        ctx: PluginContext,
    ) -> tuple[n.Document, dict[str, Path]]:
        ...

    def transform(self, document: n.Document, ctx: PluginContext) -> n.Document:
        ...


class PluginBase:
    """Default no-op plugin mixin."""

    name: str = "base"

    def render_assets(
        self,
        document: n.Document,
        ctx: PluginContext,
    ) -> tuple[n.Document, dict[str, Path]]:
        return document, {}

    def transform(self, document: n.Document, ctx: PluginContext) -> n.Document:
        return document
