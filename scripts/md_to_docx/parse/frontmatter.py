"""Minimal YAML frontmatter parser (no PyYAML)."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from md_to_docx.ast.nodes import Metadata

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_BOOL_TRUE = frozenset({"true", "yes", "1"})
_BOOL_FALSE = frozenset({"false", "no", "0"})


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse_bool(value: str) -> bool | None:
    lower = value.strip().lower()
    if lower in _BOOL_TRUE:
        return True
    if lower in _BOOL_FALSE:
        return False
    return None


def parse_frontmatter(text: str) -> tuple[Metadata, str]:
    from md_to_docx.ast.nodes import Metadata

    match = _FRONTMATTER_RE.match(text)
    if not match:
        return Metadata(), text

    body = text[match.end() :]
    raw = match.group(1)
    title = author = date = version = None
    toc: bool | None = None
    extra: list[tuple[str, str]] = []

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            print(f"warning: skipping frontmatter line: {stripped}", file=sys.stderr)
            continue
        key, _, value = stripped.partition(":")
        key = key.strip().lower()
        value = _strip_quotes(value)
        if key == "title":
            title = value or None
        elif key == "author":
            author = value or None
        elif key == "date":
            date = value or None
        elif key == "version":
            version = value or None
        elif key == "toc":
            toc = _parse_bool(value)
        else:
            extra.append((key, value))

    return Metadata(
        title=title,
        author=author,
        date=date,
        version=version,
        toc=toc,
        extra=tuple(extra),
    ), body
