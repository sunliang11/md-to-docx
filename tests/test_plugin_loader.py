"""Tests for plugin loader."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from md_to_docx.ast import nodes as n
from md_to_docx.engine.native import NativeOptions, convert_native
from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.paths import native_reference_doc
from md_to_docx.plugin.loader import load_plugins
from md_to_docx.plugins.mermaid import MermaidPlugin


def test_load_builtin_plugins() -> None:
    plugins = load_plugins()
    names = [p.name for p in plugins]
    assert "mermaid" in names
    assert "math" in names
    assert "captions" in names


def test_load_custom_plugin() -> None:
    path = Path("examples/plugins/uppercase_headings.py")
    plugins = load_plugins(extra_paths=(path,), use_builtin=False)
    assert len(plugins) == 1
    assert plugins[0].name == "uppercase_headings"


def test_uppercase_plugin_transform() -> None:
    plugins = load_plugins(
        extra_paths=("examples/plugins/uppercase_headings.py",),
        use_builtin=False,
    )
    doc = n.Document(blocks=(n.Heading(1, (n.Text("hello"),)),))
    result = plugins[0].transform(doc, None)  # type: ignore[arg-type]
    heading = result.blocks[0]
    assert isinstance(heading, n.Heading)
    assert heading.children[0].value == "HELLO"  # type: ignore[union-attr]


@pytest.mark.mermaid
def test_no_plugins_keeps_mermaid_codeblock(tmp_path: Path) -> None:
    md = tmp_path / "diagram.md"
    md.write_text("```mermaid\ngraph LR\n  A --> B\n```\n")
    out = tmp_path / "diagram.docx"
    convert_native(
        md,
        out,
        options=NativeOptions(
            template_path=native_reference_doc(),
            no_plugins=True,
        ),
    )
    from md_to_docx.parse.docx import parse_docx

    doc = parse_docx(out)
    code_blocks = [b for b in doc.blocks if isinstance(b, n.CodeBlock)]
    assert code_blocks
    assert "A --> B" in code_blocks[-1].text
