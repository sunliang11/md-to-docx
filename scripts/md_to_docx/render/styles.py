"""Default DOCX styles for native renderer."""

from __future__ import annotations

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

BODY_FONT_LATIN = "Calibri"
BODY_FONT_EAST_ASIA = "Microsoft YaHei"
MONO_FONT = "Consolas"
CODE_FILL = "F5F5F5"
HEADING_SIZES_PT = {1: 22, 2: 18, 3: 16, 4: 14, 5: 12, 6: 12}
HEADING_COLOR = RGBColor(0, 0, 0)
BODY_SIZE_PT = 11
CODE_SIZE_PT = 9


def _set_fonts(style, *, latin: str | None = None, east_asia: str | None = None) -> None:
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    if latin is not None:
        rfonts.set(qn("w:ascii"), latin)
        rfonts.set(qn("w:hAnsi"), latin)
        rfonts.set(qn("w:cs"), latin)
    if east_asia is not None:
        rfonts.set(qn("w:eastAsia"), east_asia)


def set_theme_font_lang(doc: Document, latin: str = "en-US", east_asia: str = "zh-CN") -> None:
    settings = doc.settings.element
    theme_font_lang = settings.find(qn("w:themeFontLang"))
    if theme_font_lang is None:
        theme_font_lang = OxmlElement("w:themeFontLang")
        settings.append(theme_font_lang)
    theme_font_lang.set(qn("w:val"), latin)
    theme_font_lang.set(qn("w:eastAsia"), east_asia)


def _ensure_paragraph_style(doc: Document, name: str) -> None:
    try:
        doc.styles[name]
    except KeyError:
        doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)


def _apply_heading_color(doc: Document, color: RGBColor) -> None:
    for level in range(1, 7):
        for name in (f"Heading {level}", f"Heading {level} Char"):
            try:
                style = doc.styles[name]
            except KeyError:
                continue
            style.font.color.rgb = color


def configure_document_styles(
    doc: Document,
    *,
    force: bool = False,
    heading_color: RGBColor | None = None,
) -> None:
    """Configure default styles; skip if template already has them unless force=True."""
    normal = doc.styles["Normal"]
    if force or normal.font.name is None:
        _set_fonts(normal, latin=BODY_FONT_LATIN, east_asia=BODY_FONT_EAST_ASIA)
        normal.font.size = Pt(BODY_SIZE_PT)
        normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        normal.paragraph_format.line_spacing = 1.15

    for level in range(1, 7):
        style_name = f"Heading {level}"
        try:
            hstyle = doc.styles[style_name]
        except KeyError:
            continue
        if force or hstyle.font.size is None:
            _set_fonts(hstyle, latin=BODY_FONT_LATIN, east_asia=BODY_FONT_EAST_ASIA)
            hstyle.font.size = Pt(HEADING_SIZES_PT[level])
            hstyle.font.bold = True

    if heading_color is not None:
        _apply_heading_color(doc, heading_color)

    _ensure_paragraph_style(doc, "MDCodeBlock")
    code_style = doc.styles["MDCodeBlock"]
    _set_fonts(code_style, latin=MONO_FONT, east_asia=BODY_FONT_EAST_ASIA)
    code_style.font.size = Pt(CODE_SIZE_PT)
    code_style.font.name = MONO_FONT
    pf = code_style.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    ppr = code_style.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), CODE_FILL)
    ppr.append(shd)

    _ensure_paragraph_style(doc, "Caption")
    cap = doc.styles["Caption"]
    _set_fonts(cap, latin=BODY_FONT_LATIN, east_asia=BODY_FONT_EAST_ASIA)
    cap.font.size = Pt(9)
    cap.font.italic = True
    cap.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    set_theme_font_lang(doc)
