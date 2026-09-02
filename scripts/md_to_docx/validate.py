"""Document validation without rendering."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from md_to_docx.ast import nodes as n
from md_to_docx.parse.markdown import parse_markdown

Severity = Literal["error", "warning"]


@dataclass
class Issue:
    severity: Severity
    code: str
    message: str
    line: int | None = None


def _collect_xrefs(children: tuple[n.Inline, ...]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for child in children:
        if isinstance(child, n.CrossRef):
            refs.append((child.kind, child.identifier))
        elif isinstance(child, (n.Strong, n.Emphasis, n.Strike, n.Link)):
            refs.extend(_collect_xrefs(child.children))
    return refs


def validate_document(doc: n.Document, *, base_dir: Path) -> list[Issue]:
    issues: list[Issue] = []
    if not doc.blocks:
        issues.append(Issue("error", "empty_document", "document has no content"))

    defined_fig: set[str] = set()
    defined_tbl: set[str] = set()
    used_xrefs: list[tuple[str, str]] = []
    last_heading = 0

    for block in doc.blocks:
        if isinstance(block, n.Heading):
            if block.level > last_heading + 1 and last_heading > 0:
                issues.append(
                    Issue(
                        "warning",
                        "heading_skip",
                        f"heading level jumps from H{last_heading} to H{block.level}",
                    )
                )
            last_heading = block.level
            used_xrefs.extend(_collect_xrefs(block.children))
        elif isinstance(block, n.Paragraph):
            used_xrefs.extend(_collect_xrefs(block.children))
        elif isinstance(block, n.Image):
            if block.identifier:
                defined_fig.add(block.identifier.replace("fig:", ""))
            path = base_dir / block.src if not Path(block.src).is_absolute() else Path(block.src)
            if not path.is_file():
                issues.append(
                    Issue("error", "missing_image", f"missing image: {block.src}")
                )
        elif isinstance(block, n.Mermaid):
            if not shutil.which("mmdc"):
                issues.append(
                    Issue("warning", "missing_mermaid_cli", "mmdc not on PATH for mermaid")
                )
        elif isinstance(block, n.Table):
            if block.identifier:
                defined_tbl.add(block.identifier.replace("tbl:", ""))

    for key in doc.footnotes:
        pass

    for kind, ident in used_xrefs:
        if kind == "fig" and ident not in defined_fig:
            issues.append(Issue("error", "unresolved_xref", f"unresolved fig reference: {ident}"))
        if kind == "tbl" and ident not in defined_tbl:
            issues.append(Issue("error", "unresolved_xref", f"unresolved tbl reference: {ident}"))

    return issues


def validate_file(md_path: Path, *, strict: bool = False) -> list[Issue]:
    text = md_path.read_text(encoding="utf-8")
    doc = parse_markdown(text, source_path=md_path)
    issues = validate_document(doc, base_dir=md_path.parent)
    if strict:
        issues = [
            Issue("error", i.code, i.message, i.line)
            if i.severity == "warning"
            else i
            for i in issues
        ]
    return issues
