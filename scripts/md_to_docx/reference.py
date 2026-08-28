"""Build reference-wecom.docx from pandoc default reference template."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from md_to_docx.paths import data_dir

BODY_FONT = "Microsoft YaHei"
MONO_FONT = "Consolas"


def set_east_asia_font(style, name: str) -> None:
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:cs"), name)


def configure_character_style(
    style,
    *,
    font_name: str = BODY_FONT,
    font_size: Pt | None = None,
    bold: bool | None = None,
) -> None:
    set_east_asia_font(style, font_name)
    if font_size is not None:
        style.font.size = font_size
    if bold is not None:
        style.font.bold = bold


def configure_paragraph_style(
    style,
    *,
    font_name: str = BODY_FONT,
    font_size: Pt | None = None,
    bold: bool | None = None,
    space_before: Pt | None = None,
    space_after: Pt | None = None,
    line_spacing: float | None = None,
    left_indent: Pt | None = None,
) -> None:
    configure_character_style(
        style, font_name=font_name, font_size=font_size, bold=bold
    )
    pf = style.paragraph_format
    if space_before is not None:
        pf.space_before = space_before
    if space_after is not None:
        pf.space_after = space_after
    if line_spacing is not None:
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = line_spacing
    if left_indent is not None:
        pf.left_indent = left_indent


def ensure_paragraph_style(doc: Document, name: str, base: str = "Normal") -> None:
    try:
        doc.styles[name]
    except KeyError:
        doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        doc.styles[name].base_style = doc.styles[base]


def ensure_character_style(doc: Document, name: str, base: str = "Default Paragraph Font") -> None:
    try:
        doc.styles[name]
    except KeyError:
        doc.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
        doc.styles[name].base_style = doc.styles[base]


def add_left_border(style, color: str = "D9D9D9", size: int = 12) -> None:
    ppr = style.element.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), str(size))
    left.set(qn("w:space"), "4")
    left.set(qn("w:color"), color)
    p_bdr.append(left)
    ppr.append(p_bdr)


def configure_table_style(doc: Document) -> None:
    table_style = doc.styles["Table"]
    configure_paragraph_style(
        table_style,
        font_size=Pt(10),
        space_before=Pt(0),
        space_after=Pt(0),
    )

    ensure_paragraph_style(doc, "Compact Table", base="Table")
    compact = doc.styles["Compact Table"]
    configure_paragraph_style(
        compact,
        font_size=Pt(9),
        space_before=Pt(0),
        space_after=Pt(0),
    )


def build_reference_doc(output_dir: Path | None = None) -> Path:
    assets = output_dir or data_dir()
    assets.mkdir(parents=True, exist_ok=True)
    default_ref = assets / "reference-default.docx"
    output_ref = assets / "reference-wecom.docx"

    if not default_ref.is_file():
        subprocess.run(
            [
                "pandoc",
                "--print-default-data-file",
                "reference.docx",
                "-o",
                str(default_ref),
            ],
            check=True,
        )

    shutil.copy2(default_ref, output_ref)
    doc = Document(str(output_ref))

    # Body
    configure_paragraph_style(
        doc.styles["Normal"],
        font_size=Pt(11),
        space_after=Pt(6),
        line_spacing=1.5,
    )
    configure_paragraph_style(
        doc.styles["Body Text"],
        font_size=Pt(11),
        space_after=Pt(6),
        line_spacing=1.5,
    )
    configure_paragraph_style(
        doc.styles["First Paragraph"],
        font_size=Pt(11),
        space_after=Pt(6),
        line_spacing=1.5,
    )
    configure_paragraph_style(
        doc.styles["Compact"],
        font_size=Pt(10),
        space_after=Pt(3),
        line_spacing=1.25,
    )

    # Headings
    heading_specs = [
        ("Heading 1", Pt(18), Pt(18), Pt(12)),
        ("Heading 2", Pt(16), Pt(14), Pt(8)),
        ("Heading 3", Pt(14), Pt(12), Pt(6)),
        ("Heading 4", Pt(13), Pt(10), Pt(4)),
    ]
    for name, size, before, after in heading_specs:
        configure_paragraph_style(
            doc.styles[name],
            font_size=size,
            bold=True,
            space_before=before,
            space_after=after,
            line_spacing=1.25,
        )
        char_name = f"{name} Char"
        if char_name in [s.name for s in doc.styles]:
            configure_character_style(
                doc.styles[char_name], font_size=size, bold=True
            )

    # Blockquote
    configure_paragraph_style(
        doc.styles["Block Text"],
        font_size=Pt(11),
        space_before=Pt(6),
        space_after=Pt(6),
        line_spacing=1.5,
        left_indent=Pt(18),
    )
    add_left_border(doc.styles["Block Text"])

    # Code block
    ensure_paragraph_style(doc, "Source Code", base="Body Text")
    configure_paragraph_style(
        doc.styles["Source Code"],
        font_name=MONO_FONT,
        font_size=Pt(10),
        space_before=Pt(6),
        space_after=Pt(6),
        line_spacing=1.15,
        left_indent=Pt(0),
    )
    doc.styles["Source Code"].font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Inline code
    ensure_character_style(doc, "Verbatim Char")
    set_east_asia_font(doc.styles["Verbatim Char"], MONO_FONT)
    doc.styles["Verbatim Char"].font.size = Pt(10)
    doc.styles["Verbatim Char"].font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # Lists
    if "List Paragraph" in [s.name for s in doc.styles]:
        configure_paragraph_style(
            doc.styles["List Paragraph"],
            font_size=Pt(11),
            space_after=Pt(3),
            line_spacing=1.5,
        )

    configure_table_style(doc)

    doc.save(str(output_ref))
    print(f"built: {output_ref}")
    return output_ref


def main() -> int:
    try:
        build_reference_doc()
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
