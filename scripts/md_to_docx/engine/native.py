"""Native engine: parse AST and render DOCX."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.plugin.base import PluginContext
from md_to_docx.plugin.loader import load_plugins
from md_to_docx.render.docx_renderer import render_docx
from md_to_docx.transform.numbering import apply_heading_numbers
from md_to_docx.transform.outline import insert_toc
from md_to_docx.transform.xrefs import resolve_xrefs


@dataclass
class NativeOptions:
    normalize: bool = True
    template_path: Path | None = None
    toc: bool = False
    toc_title: str = "Contents"
    numbering: bool = False
    title: str | None = None
    author: str | None = None
    date: str | None = None
    doc_version: str | None = None
    page_numbers: bool = True
    strict_mermaid: bool = False
    figure_label: str = "Figure"
    table_label: str = "Table"
    section_label: str = "Section"
    plugin_paths: tuple[str | Path, ...] = ()
    no_plugins: bool = False


def convert_native(md_path: Path, out_docx: Path, *, options: NativeOptions | None = None) -> None:
    opts = options or NativeOptions()
    text = md_path.read_text(encoding="utf-8")
    if opts.normalize:
        from md_to_docx.converter import normalize_md

        text = normalize_md(text)

    doc = parse_markdown(text, source_path=md_path)
    meta = doc.metadata

    if opts.toc or meta.toc:
        doc = insert_toc(doc, title=opts.toc_title)
    if opts.numbering:
        doc = apply_heading_numbers(doc, enabled=True)

    plugins = load_plugins(
        extra_paths=opts.plugin_paths,
        use_builtin=not opts.no_plugins,
    )
    ctx = PluginContext(
        base_dir=md_path.parent,
        config={"md_path": str(md_path)},
        strict_mermaid=opts.strict_mermaid,
        figure_label=opts.figure_label,
        table_label=opts.table_label,
    )
    media_paths: dict[str, Path] = {}
    for plugin in plugins:
        doc, new_media = plugin.render_assets(doc, ctx)
        media_paths.update(new_media)
        doc = plugin.transform(doc, ctx)

    xref_map = ctx.config.get("xref_map", {})
    if not opts.no_plugins:
        doc = resolve_xrefs(doc, xref_map)

    render_docx(
        doc,
        out_docx,
        base_dir=md_path.parent,
        template_path=opts.template_path,
        title=opts.title or meta.title,
        author=opts.author or meta.author,
        date=opts.date or meta.date,
        version=opts.doc_version or meta.version,
        page_numbers=opts.page_numbers,
        figure_label=opts.figure_label,
        table_label=opts.table_label,
        section_label=opts.section_label,
        xref_map=xref_map,
        media_paths=media_paths,
    )
    print(f"ok: {md_path} -> {out_docx}")
