"""Tests for docx output quality (XML assertions)."""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from md_to_docx.converter import convert_one

# Namespaces for Word XML
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def extract_docx_xml(docx_path: Path, xml_file: str) -> etree.Element:
    """Extract and parse an XML file from a .docx archive."""
    with zipfile.ZipFile(docx_path, "r") as zf:
        with zf.open(xml_file) as f:
            return etree.parse(f).getroot()


def get_paragraph_style(para_elem) -> str | None:
    """Extract paragraph style name from a paragraph element."""
    ppr = para_elem.find("w:pPr", namespaces=NAMESPACES)
    if ppr is None:
        return None
    pstyle = ppr.find("w:pStyle", namespaces=NAMESPACES)
    if pstyle is None:
        return None
    return pstyle.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")


def get_table_style(tbl_elem) -> str | None:
    """Extract table style from a table element."""
    tbl_pr = tbl_elem.find("w:tblPr", namespaces=NAMESPACES)
    if tbl_pr is None:
        return None
    tbl_style = tbl_pr.find("w:tblStyle", namespaces=NAMESPACES)
    if tbl_style is None:
        return None
    return tbl_style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")


def has_table_borders(tbl_elem) -> bool:
    """Check if table has tblBorders element."""
    tbl_pr = tbl_elem.find("w:tblPr", namespaces=NAMESPACES)
    if tbl_pr is None:
        return False
    tbl_borders = tbl_pr.find("w:tblBorders", namespaces=NAMESPACES)
    return tbl_borders is not None


def get_font_info(r_elem) -> dict[str, str | None]:
    """Extract font information from a run element."""
    rpr = r_elem.find("w:rPr", namespaces=NAMESPACES)
    if rpr is None:
        return {}
    
    rfonts = rpr.find("w:rFonts", namespaces=NAMESPACES)
    if rfonts is None:
        return {}
    
    return {
        "ascii": rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"),
        "eastAsia": rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia"),
        "hAnsi": rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"),
    }


@pytest.fixture
def converted_comprehensive_docx(tmp_path: Path) -> Path:
    """Convert comprehensive.md to docx and return the path."""
    import shutil
    from md_to_docx.paths import bundled_conversion_assets
    
    fixture_md = Path(__file__).parent / "fixtures" / "comprehensive.md"
    temp_md = tmp_path / "comprehensive.md"
    shutil.copy(fixture_md, temp_md)
    
    # Check if pandoc is available
    pandoc = shutil.which("pandoc")
    if not pandoc:
        pytest.skip("pandoc not available")
    
    with bundled_conversion_assets() as (reference_doc, lua_filter):
        convert_one(
            temp_md,
            pandoc,
            reference_doc,
            lua_filter,
            None,  # mmdc
            None,  # puppeteer_config
            4.0,   # scale
            None,  # mermaid_width
        )
    
    return temp_md.with_suffix(".docx")


def test_code_block_has_source_code_style(converted_comprehensive_docx: Path):
    """Language-tagged code blocks should get Source Code paragraph style."""
    doc_xml = extract_docx_xml(converted_comprehensive_docx, "word/document.xml")
    
    # Find all paragraphs
    paragraphs = doc_xml.findall(".//w:p", namespaces=NAMESPACES)
    
    # Look for code block paragraphs (they contain "def hello_world" or similar)
    code_para_styles = []
    for para in paragraphs:
        text_content = "".join(para.itertext())
        if "def hello_world" in text_content or "print(hello_world" in text_content:
            style = get_paragraph_style(para)
            if style:
                code_para_styles.append(style)
    
    # At least one code paragraph should have Source Code style
    # (Some might be SourceCode or Source Code depending on pandoc version)
    assert any("Source" in style and "Code" in style for style in code_para_styles), \
        f"Expected code blocks to have Source Code style, got: {code_para_styles}"


def test_table_style_has_borders(converted_comprehensive_docx: Path):
    """Table styles in the reference should have tblBorders defined."""
    styles_xml = extract_docx_xml(converted_comprehensive_docx, "word/styles.xml")
    
    styles = styles_xml.findall(".//w:style", namespaces=NAMESPACES)
    table_style = None
    for style in styles:
        style_id = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId")
        style_type = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type")
        if style_type == "table" and style_id == "Table":
            table_style = style
            break
    
    assert table_style is not None, "Table style not found in styles.xml"
    
    tbl_pr = table_style.find("w:tblPr", namespaces=NAMESPACES)
    assert tbl_pr is not None, "Table style should have tblPr"
    
    borders = tbl_pr.find("w:tblBorders", namespaces=NAMESPACES)
    assert borders is not None, "Table style should have tblBorders defined"
    
    # Check all border sides are present
    border_sides = [el.tag.split("}")[1] for el in borders]
    assert "top" in border_sides
    assert "left" in border_sides
    assert "bottom" in border_sides
    assert "right" in border_sides
    assert "insideH" in border_sides
    assert "insideV" in border_sides


def test_compact_table_style_exists(converted_comprehensive_docx: Path):
    """CompactTable style should exist and have borders."""
    styles_xml = extract_docx_xml(converted_comprehensive_docx, "word/styles.xml")
    
    styles = styles_xml.findall(".//w:style", namespaces=NAMESPACES)
    compact_style = None
    for style in styles:
        style_id = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId")
        style_type = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type")
        if style_type == "table" and style_id == "CompactTable":
            compact_style = style
            break
    
    assert compact_style is not None, "CompactTable style not found in styles.xml"
    
    tbl_pr = compact_style.find("w:tblPr", namespaces=NAMESPACES)
    assert tbl_pr is not None, "CompactTable style should have tblPr"
    
    borders = tbl_pr.find("w:tblBorders", namespaces=NAMESPACES)
    assert borders is not None, "CompactTable style should have tblBorders defined"


def test_body_text_has_yahei_font(converted_comprehensive_docx: Path):
    """Body paragraphs should use Microsoft YaHei for eastAsia font."""
    styles_xml = extract_docx_xml(converted_comprehensive_docx, "word/styles.xml")
    
    # Find Normal style
    styles = styles_xml.findall(".//w:style", namespaces=NAMESPACES)
    normal_style = None
    for style in styles:
        style_id = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId")
        if style_id == "Normal":
            normal_style = style
            break
    
    assert normal_style is not None, "Normal style not found"
    
    # Check rPr -> rFonts
    rpr = normal_style.find(".//w:rPr", namespaces=NAMESPACES)
    assert rpr is not None, "Normal style should have rPr"
    
    rfonts = rpr.find("w:rFonts", namespaces=NAMESPACES)
    assert rfonts is not None, "Normal style should have rFonts"
    
    east_asia = rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia")
    assert east_asia == "Microsoft YaHei", \
        f"Expected Microsoft YaHei for eastAsia font, got: {east_asia}"


def test_code_has_consolas_and_yahei(converted_comprehensive_docx: Path):
    """Code styles should use Consolas for latin and YaHei for eastAsia."""
    styles_xml = extract_docx_xml(converted_comprehensive_docx, "word/styles.xml")
    
    # Find Source Code style
    styles = styles_xml.findall(".//w:style", namespaces=NAMESPACES)
    code_style = None
    for style in styles:
        style_id = style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId")
        # Could be SourceCode or Source Code
        if style_id and ("Source" in style_id and "Code" in style_id):
            code_style = style
            break
    
    assert code_style is not None, "Source Code style not found"
    
    rpr = code_style.find(".//w:rPr", namespaces=NAMESPACES)
    assert rpr is not None, "Source Code style should have rPr"
    
    rfonts = rpr.find("w:rFonts", namespaces=NAMESPACES)
    assert rfonts is not None, "Source Code style should have rFonts"
    
    ascii_font = rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii")
    east_asia = rfonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia")
    
    assert ascii_font == "Consolas", f"Expected Consolas for ascii font, got: {ascii_font}"
    assert east_asia == "Microsoft YaHei", \
        f"Expected Microsoft YaHei for eastAsia font in code, got: {east_asia}"


def test_heading_5_and_6_exist(converted_comprehensive_docx: Path):
    """Heading 5 and Heading 6 styles should exist in the document."""
    styles_xml = extract_docx_xml(converted_comprehensive_docx, "word/styles.xml")
    
    styles = styles_xml.findall(".//w:style", namespaces=NAMESPACES)
    style_ids = {
        style.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId")
        for style in styles
    }
    
    assert "Heading5" in style_ids or "Heading 5" in style_ids, "Heading 5 style not found"
    assert "Heading6" in style_ids or "Heading 6" in style_ids, "Heading 6 style not found"


def test_document_has_chinese_theme_lang(converted_comprehensive_docx: Path):
    """Document settings should include zh-CN for eastAsia theme language."""
    settings_xml = extract_docx_xml(converted_comprehensive_docx, "word/settings.xml")
    
    theme_font_lang = settings_xml.find(".//w:themeFontLang", namespaces=NAMESPACES)
    assert theme_font_lang is not None, "themeFontLang element not found"
    
    east_asia = theme_font_lang.get(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia"
    )
    assert east_asia == "zh-CN", \
        f"Expected zh-CN for eastAsia theme language, got: {east_asia}"
