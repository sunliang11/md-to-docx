"""Document AST node types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union

Alignment = Literal["left", "center", "right", "default"]


@dataclass(frozen=True, slots=True)
class Text:
    value: str


@dataclass(frozen=True, slots=True)
class Strong:
    children: tuple[Inline, ...]


@dataclass(frozen=True, slots=True)
class Emphasis:
    children: tuple[Inline, ...]


@dataclass(frozen=True, slots=True)
class Strike:
    children: tuple[Inline, ...]


@dataclass(frozen=True, slots=True)
class Code:
    value: str


@dataclass(frozen=True, slots=True)
class Link:
    href: str
    children: tuple[Inline, ...]
    title: str | None = None


@dataclass(frozen=True, slots=True)
class InlineImage:
    src: str
    alt: str = ""
    title: str | None = None


@dataclass(frozen=True, slots=True)
class Break:
    """Hard line break."""


@dataclass(frozen=True, slots=True)
class SoftBreak:
    pass


@dataclass(frozen=True, slots=True)
class MathInline:
    latex: str


Inline = Union[
    Text, Strong, Emphasis, Strike, Code, Link, InlineImage, Break, SoftBreak, MathInline,
    "CrossRef", "FootnoteRef",
]


@dataclass(frozen=True, slots=True)
class Heading:
    level: int
    children: tuple[Inline, ...]
    anchor: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 6:
            raise ValueError(f"heading level must be 1-6, got {self.level}")


@dataclass(frozen=True, slots=True)
class Paragraph:
    children: tuple[Inline, ...]


@dataclass(frozen=True, slots=True)
class ListItem:
    children: tuple[Block, ...]
    checked: bool | None = None


@dataclass(frozen=True, slots=True)
class ListBlock:
    ordered: bool
    items: tuple[ListItem, ...]
    start: int = 1
    tight: bool = True


@dataclass(frozen=True, slots=True)
class TableCell:
    children: tuple[Block, ...]
    align: Alignment = "default"
    header: bool = False


@dataclass(frozen=True, slots=True)
class Table:
    rows: tuple[tuple[TableCell, ...], ...]
    identifier: str | None = None
    caption: str | None = None


@dataclass(frozen=True, slots=True)
class CodeBlock:
    text: str
    lang: str | None = None


@dataclass(frozen=True, slots=True)
class Mermaid:
    source: str
    diagram_hint: str | None = None


@dataclass(frozen=True, slots=True)
class MathBlock:
    latex: str


@dataclass(frozen=True, slots=True)
class BlockQuote:
    children: tuple[Block, ...]


@dataclass(frozen=True, slots=True)
class ThematicBreak:
    pass


@dataclass(frozen=True, slots=True)
class Image:
    src: str
    alt: str = ""
    title: str | None = None
    identifier: str | None = None


@dataclass(frozen=True, slots=True)
class Figure:
    image: Image | Mermaid
    caption: str
    identifier: str
    number: int | None = None


@dataclass(frozen=True, slots=True)
class PageBreak:
    pass


@dataclass(frozen=True, slots=True)
class TableOfContents:
    levels: int = 3
    title: str = "Contents"


@dataclass(frozen=True, slots=True)
class HTMLBlock:
    raw: str


@dataclass(frozen=True, slots=True)
class CrossRef:
    kind: Literal["fig", "tbl", "sec"]
    identifier: str


@dataclass(frozen=True, slots=True)
class FootnoteRef:
    key: str


@dataclass(frozen=True, slots=True)
class FootnoteDef:
    key: str
    children: tuple[Block, ...]


Block = Union[
    Heading, Paragraph, ListBlock, Table, CodeBlock, BlockQuote,
    ThematicBreak, Image, PageBreak, HTMLBlock, Mermaid, MathBlock,
    Figure, TableOfContents,
]


@dataclass(frozen=True, slots=True)
class Metadata:
    title: str | None = None
    author: str | None = None
    date: str | None = None
    version: str | None = None
    toc: bool | None = None
    extra: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Document:
    blocks: tuple[Block, ...]
    metadata: Metadata = field(default_factory=Metadata)
    footnotes: tuple[FootnoteDef, ...] = ()
