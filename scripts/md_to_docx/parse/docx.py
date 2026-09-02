"""DOCX → Document AST parser."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

from md_to_docx.ast import nodes as n

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

NS = {"w": W_NS, "r": R_NS, "a": A_NS, "wp": WP_NS, "m": M_NS}

HEADING_STYLES: dict[str, int] = {}
for i in range(1, 7):
    HEADING_STYLES[f"Heading {i}"] = i
    HEADING_STYLES[f"Heading{i}"] = i
TOC_INSTR_RE = re.compile(r"\bTOC\b", re.I)
HEADING_NAME_RE = re.compile(r"^(?:heading|标题)\s*(\d+)$", re.IGNORECASE)


def _heading_level_from_name(name: str | None) -> int | None:
    if not name:
        return None
    if name in HEADING_STYLES:
        return HEADING_STYLES[name]
    match = HEADING_NAME_RE.match(name.strip())
    if match:
        level = int(match.group(1))
        if 1 <= level <= 6:
            return level
    return None


def _outline_lvl_to_heading(val: str | None) -> int | None:
    if val is None:
        return None
    try:
        outline = int(val)
    except ValueError:
        return None
    if 0 <= outline <= 5:
        return outline + 1
    return None


def _builtin_heading_level(style_id: str) -> int | None:
    if style_id in HEADING_STYLES:
        return HEADING_STYLES[style_id]
    level = _heading_level_from_name(style_id)
    if level is not None:
        return level
    if style_id.isdigit():
        numeric = int(style_id)
        if 1 <= numeric <= 6:
            return numeric
    return None


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _m(tag: str) -> str:
    return f"{{{M_NS}}}{tag}"


def _a(tag: str) -> str:
    return f"{{{A_NS}}}{tag}"


def _r(tag: str) -> str:
    return f"{{{R_NS}}}{tag}"


class DocxParser:
    def __init__(self, docx_path: Path) -> None:
        self.docx_path = docx_path.resolve()
        self.media_dir = self.docx_path.parent / f"{self.docx_path.stem}-media"
        self._rels: dict[str, str] = {}
        self._footnotes: dict[str, list[n.Block]] = {}
        self._warnings: list[str] = []
        self._style_heading_levels: dict[str, int] = {}

    def warn(self, msg: str) -> None:
        self._warnings.append(msg)
        print(f"warning: {msg}", file=sys.stderr)

    def parse(self) -> n.Document:
        with zipfile.ZipFile(self.docx_path, "r") as zf:
            self._load_relationships(zf)
            self._load_styles(zf)
            self._load_footnotes(zf)
            with zf.open("word/document.xml") as f:
                root = etree.parse(f).getroot()
            self._extract_media(zf)

        body = root.find("w:body", NS)
        if body is None:
            return n.Document(blocks=())

        blocks: list[n.Block] = []
        footnote_defs: list[n.FootnoteDef] = []

        for child in body:
            tag = etree.QName(child).localname
            if tag == "p":
                parsed = self._parse_paragraph(child)
                if parsed is None:
                    continue
                if isinstance(parsed, list):
                    blocks.extend(parsed)
                else:
                    blocks.append(parsed)
            elif tag == "tbl":
                blocks.append(self._parse_table(child))
            elif tag == "sectPr":
                pass
            else:
                self.warn(f"unsupported body element: {tag}")

        for key, fblocks in self._footnotes.items():
            footnote_defs.append(n.FootnoteDef(key=key, children=tuple(fblocks)))

        return n.Document(blocks=tuple(blocks), footnotes=tuple(footnote_defs))

    def _load_relationships(self, zf: zipfile.ZipFile) -> None:
        try:
            with zf.open("word/_rels/document.xml.rels") as f:
                root = etree.parse(f).getroot()
            for rel in root:
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                    self._rels[rid] = target
        except KeyError:
            pass

    def _load_styles(self, zf: zipfile.ZipFile) -> None:
        try:
            with zf.open("word/styles.xml") as f:
                root = etree.parse(f).getroot()
        except KeyError:
            return

        styles: dict[str, dict[str, str | int | None]] = {}
        for style_el in root.findall("w:style", NS):
            style_id = style_el.get(_w("styleId"))
            if not style_id:
                continue
            name_el = style_el.find("w:name", NS)
            name = name_el.get(_w("val")) if name_el is not None else None
            based_on_el = style_el.find("w:basedOn", NS)
            based_on = based_on_el.get(_w("val")) if based_on_el is not None else None
            link_el = style_el.find("w:link", NS)
            link = link_el.get(_w("val")) if link_el is not None else None
            outline = None
            ppr = style_el.find("w:pPr", NS)
            if ppr is not None:
                outline_el = ppr.find("w:outlineLvl", NS)
                if outline_el is not None:
                    outline = _outline_lvl_to_heading(outline_el.get(_w("val")))
            styles[style_id] = {
                "name": name,
                "based_on": based_on,
                "link": link,
                "outline": outline,
            }

        self._style_heading_levels = {}
        for style_id in styles:
            level = self._resolve_style_heading_level(style_id, styles)
            if level is not None:
                self._style_heading_levels[style_id] = level

    def _resolve_style_heading_level(
        self,
        style_id: str,
        styles: dict[str, dict[str, str | int | None]],
        *,
        seen: set[str] | None = None,
    ) -> int | None:
        if style_id in HEADING_STYLES:
            return HEADING_STYLES[style_id]

        if seen is None:
            seen = set()
        if style_id in seen:
            return None
        seen.add(style_id)

        info = styles.get(style_id)
        if info is None:
            return _builtin_heading_level(style_id)

        level = _heading_level_from_name(info.get("name"))  # type: ignore[arg-type]
        if level is not None:
            return level

        outline = info.get("outline")
        if isinstance(outline, int):
            return outline

        based_on = info.get("based_on")
        if isinstance(based_on, str):
            level = self._resolve_style_heading_level(based_on, styles, seen=seen)
            if level is not None:
                return level

        link = info.get("link")
        if isinstance(link, str):
            level = self._resolve_style_heading_level(link, styles, seen=seen)
            if level is not None:
                return level

        return None

    def _paragraph_outline_level(self, p: etree._Element) -> int | None:
        ppr = p.find("w:pPr", NS)
        if ppr is None:
            return None
        outline_el = ppr.find("w:outlineLvl", NS)
        if outline_el is None:
            return None
        return _outline_lvl_to_heading(outline_el.get(_w("val")))

    def _heading_level_for_paragraph(
        self, p: etree._Element, style: str | None
    ) -> int | None:
        level = None
        if style:
            level = HEADING_STYLES.get(style) or self._style_heading_levels.get(style)
        if level is None:
            level = self._paragraph_outline_level(p)
        return level

    def _load_footnotes(self, zf: zipfile.ZipFile) -> None:
        try:
            with zf.open("word/footnotes.xml") as f:
                root = etree.parse(f).getroot()
        except KeyError:
            return
        for fn in root.findall("w:footnote", NS):
            fn_id = fn.get(_w("id"))
            if fn_id in (None, "-1", "0"):
                continue
            fblocks: list[n.Block] = []
            for child in fn:
                if etree.QName(child).localname == "p":
                    parsed = self._parse_paragraph(child, in_footnote=True)
                    if parsed is None:
                        continue
                    if isinstance(parsed, list):
                        fblocks.extend(parsed)
                    else:
                        fblocks.append(parsed)
            if fblocks:
                self._footnotes[fn_id] = fblocks

    def _extract_media(self, zf: zipfile.ZipFile) -> None:
        self.media_dir.mkdir(parents=True, exist_ok=True)
        for name in zf.namelist():
            if name.startswith("word/media/"):
                dest = self.media_dir / Path(name).name
                if not dest.exists():
                    dest.write_bytes(zf.read(name))

    def _paragraph_style(self, p: etree._Element) -> str | None:
        ppr = p.find("w:pPr", NS)
        if ppr is None:
            return None
        pstyle = ppr.find("w:pStyle", NS)
        if pstyle is None:
            return None
        return pstyle.get(_w("val"))

    def _is_toc_paragraph(self, p: etree._Element) -> bool:
        for instr in p.iter(_w("instrText")):
            if instr.text and TOC_INSTR_RE.search(instr.text):
                return True
        return False

    def _has_page_break(self, p: etree._Element) -> bool:
        for br in p.iter(_w("br")):
            if br.get(_w("type")) == "page":
                return True
        for el in p.iter():
            if etree.QName(el).localname == "lastRenderedPageBreak":
                return True
        return False

    def _parse_paragraph(
        self, p: etree._Element, *, in_footnote: bool = False
    ) -> n.Block | list[n.Block] | None:
        if self._is_toc_paragraph(p):
            self.warn("skipping TOC field paragraph")
            return None

        if self._has_page_break(p) and not list(p.iter(_w("t"))):
            return n.PageBreak()

        style = self._paragraph_style(p)
        inlines = self._parse_inlines(p)

        if style == "MDCodeBlock":
            text = self._inline_text(inlines)
            if not text.strip():
                return None
            return n.CodeBlock(text.rstrip("\n"), lang=None)

        level = self._heading_level_for_paragraph(p, style)
        if level is not None:
            if not inlines:
                return None
            return n.Heading(level, inlines)

        if style in ("List Number", "List Bullet"):
            ordered = style == "List Number"
            return n.ListBlock(
                ordered=ordered,
                items=(n.ListItem(children=(n.Paragraph(inlines),)),),
            )

        ppr = p.find("w:pPr", NS)
        if ppr is not None and ppr.find("w:numPr", NS) is not None:
            ilvl_el = ppr.find("w:numPr/w:ilvl", NS)
            numid_el = ppr.find("w:numPr/w:numId", NS)
            ordered = True
            if numid_el is not None:
                num_val = numid_el.get(_w("val"), "1")
                ordered = num_val != "2"
            return n.ListBlock(
                ordered=ordered,
                items=(n.ListItem(children=(n.Paragraph(inlines),)),),
            )

        if style == "Caption":
            text = self._inline_text(inlines)
            return n.Paragraph((n.Text(text),))

        if inlines or style is None or style == "Normal":
            blocks: list[n.Block] = []
            if self._has_page_break(p):
                blocks.append(n.PageBreak())
            if inlines:
                blocks.append(n.Paragraph(inlines))
            if not blocks:
                return None
            return blocks[0] if len(blocks) == 1 else blocks

        if style and style in self._style_heading_levels:
            if not inlines:
                return None
            return n.Heading(self._style_heading_levels[style], inlines)

        self.warn(f"unhandled paragraph style: {style}")
        if inlines:
            return n.Paragraph(inlines)
        return None

    def _inline_text(self, inlines: tuple[n.Inline, ...]) -> str:
        parts: list[str] = []
        for child in inlines:
            if isinstance(child, n.Text):
                parts.append(child.value)
            elif isinstance(child, n.Code):
                parts.append(child.value)
            elif isinstance(child, (n.Strong, n.Emphasis, n.Strike)):
                parts.append(self._inline_text(child.children))
            elif isinstance(child, n.SoftBreak):
                parts.append(" ")
            elif isinstance(child, n.Break):
                parts.append("\n")
        return "".join(parts)

    def _parse_inlines(self, parent: etree._Element) -> tuple[n.Inline, ...]:
        children: list[n.Inline] = []
        for child in parent:
            tag = etree.QName(child).localname
            if tag == "r":
                children.extend(self._parse_run(child))
            elif tag == "hyperlink":
                children.append(self._parse_hyperlink(child))
            elif tag in ("oMath", "oMathPara"):
                math = self._parse_math(child)
                if math:
                    children.append(math)
            elif tag == "bookmarkStart":
                pass
            elif tag == "bookmarkEnd":
                pass
            elif tag == "fldSimple":
                text = "".join(child.itertext())
                if text.strip():
                    children.append(n.Text(text))
            else:
                local = etree.QName(child).localname
                if local not in ("pPr",):
                    self.warn(f"unsupported inline element: {local}")
        return tuple(children)

    def _parse_run(self, r: etree._Element) -> list[n.Inline]:
        rpr = r.find("w:rPr", NS)
        bold = italic = strike = code = False
        if rpr is not None:
            bold = rpr.find("w:b", NS) is not None
            italic = rpr.find("w:i", NS) is not None
            strike = rpr.find("w:strike", NS) is not None
            rfonts = rpr.find("w:rFonts", NS)
            if rfonts is not None:
                font = rfonts.get(_w("ascii")) or rfonts.get(_w("hAnsi"))
                if font == "Consolas":
                    code = True

        results: list[n.Inline] = []
        for child in r:
            tag = etree.QName(child).localname
            if tag == "t":
                text = child.text or ""
                if text:
                    inline: n.Inline = n.Text(text)
                    if code:
                        inline = n.Code(text)
                    elif strike:
                        inline = n.Strike((n.Text(text),))
                    elif bold:
                        inline = n.Strong((n.Text(text),))
                    elif italic:
                        inline = n.Emphasis((n.Text(text),))
                    results.append(inline)
            elif tag == "br":
                br_type = child.get(_w("type"))
                if br_type == "page":
                    pass
                else:
                    results.append(n.Break())
            elif tag == "tab":
                results.append(n.Text("\t"))
            elif tag == "drawing":
                img = self._parse_drawing(child)
                if img:
                    results.append(img)
            elif tag in ("oMath",):
                math = self._parse_math(child)
                if math:
                    results.append(math)
            elif tag == "footnoteReference":
                fn_id = child.get(_w("id"), "")
                results.append(n.FootnoteRef(fn_id))

        return results

    def _parse_hyperlink(self, hl: etree._Element) -> n.Link:
        rid = hl.get(_r("id"))
        href = self._rels.get(rid, "") if rid else ""
        if href and not href.startswith("http"):
            href = f"file://{href}"
        inlines: list[n.Inline] = []
        for r in hl.findall("w:r", NS):
            inlines.extend(self._parse_run(r))
        return n.Link(href, tuple(inlines))

    def _parse_drawing(self, drawing: etree._Element) -> n.InlineImage | None:
        blip = drawing.find(".//a:blip", NS)
        if blip is None:
            self.warn("drawing without blip — skipped")
            return None
        embed = blip.get(_r("embed"))
        if not embed:
            return None
        target = self._rels.get(embed, "")
        if not target:
            return None
        media_name = Path(target).name
        src = f"{self.docx_path.stem}-media/{media_name}"
        return n.InlineImage(src=src, alt="")

    def _parse_math(self, el: etree._Element) -> n.MathInline | None:
        text = "".join(el.itertext()).strip()
        if not text:
            return None
        return n.MathInline(text)

    def _parse_table(self, tbl: etree._Element) -> n.Table:
        rows: list[tuple[n.TableCell, ...]] = []
        for tr in tbl.findall("w:tr", NS):
            cells: list[n.TableCell] = []
            for tc in tr.findall("w:tc", NS):
                cell_blocks: list[n.Block] = []
                for p in tc.findall("w:p", NS):
                    parsed = self._parse_paragraph(p)
                    if parsed is None:
                        continue
                    if isinstance(parsed, list):
                        cell_blocks.extend(parsed)
                    else:
                        cell_blocks.append(parsed)
                if not cell_blocks:
                    cell_blocks = [n.Paragraph(())]
                cells.append(n.TableCell(children=tuple(cell_blocks)))
            if cells:
                rows.append(tuple(cells))
        return n.Table(rows=tuple(rows))

    def _block_image(self, p: etree._Element) -> n.Image | None:
        for drawing in p.iter(_w("drawing")):
            blip = drawing.find(".//a:blip", NS)
            if blip is None:
                continue
            embed = blip.get(_r("embed"))
            if not embed:
                continue
            target = self._rels.get(embed, "")
            if target:
                media_name = Path(target).name
                return n.Image(src=f"{self.docx_path.stem}-media/{media_name}")
        return None


def parse_docx(path: Path) -> n.Document:
    """Parse a DOCX file into a Document AST."""
    return DocxParser(path).parse()
