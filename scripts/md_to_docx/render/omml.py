"""MathML to OMML conversion."""

from __future__ import annotations

import sys
from xml.etree import ElementTree as ET

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _omml_tag(name: str) -> str:
    return f"{{{MATH_NS}}}{name}"


def _mathml_to_omml(mathml: str) -> ET.Element | None:
    try:
        root = ET.fromstring(mathml)
    except ET.ParseError:
        return None

    def convert(node: ET.Element) -> ET.Element | None:
        tag = node.tag.split("}")[-1] if "}" in node.tag else node.tag
        if tag == "math":
            omath = ET.Element(_omml_tag("oMath"))
            for child in node:
                c = convert(child)
                if c is not None:
                    omath.append(c)
            return omath
        if tag in ("mi", "mn", "mo"):
            r = ET.Element(_omml_tag("r"))
            t = ET.Element(_omml_tag("t"))
            t.text = (node.text or "") + "".join(
                ET.tostring(c, encoding="unicode") for c in node
            )
            if not t.text and node.text is None:
                t.text = ""
            r.append(t)
            return r
        if tag == "mfrac":
            f = ET.Element(_omml_tag("f"))
            num = ET.Element(_omml_tag("num"))
            den = ET.Element(_omml_tag("den"))
            children = list(node)
            if len(children) >= 2:
                c0 = convert(children[0])
                c1 = convert(children[1])
                if c0 is not None:
                    num.append(c0)
                if c1 is not None:
                    den.append(c1)
            f.append(num)
            f.append(den)
            return f
        if tag == "msup":
            s = ET.Element(_omml_tag("sSup"))
            e = ET.Element(_omml_tag("e"))
            sup = ET.Element(_omml_tag("sup"))
            children = list(node)
            if children:
                c0 = convert(children[0])
                if c0 is not None:
                    e.append(c0)
            if len(children) > 1:
                c1 = convert(children[1])
                if c1 is not None:
                    sup.append(c1)
            s.append(e)
            s.append(sup)
            return s
        if tag == "msqrt":
            rad = ET.Element(_omml_tag("rad"))
            deg = ET.Element(_omml_tag("deg"))
            e = ET.Element(_omml_tag("e"))
            for child in node:
                c = convert(child)
                if c is not None:
                    e.append(c)
            rad.append(deg)
            rad.append(e)
            return rad
        if tag == "mrow":
            omath = ET.Element(_omml_tag("oMath"))
            for child in node:
                c = convert(child)
                if c is not None:
                    omath.append(c)
            return omath
        return None

    return convert(root)


def _insert_omml(paragraph: Paragraph, omath_el: ET.Element) -> None:
    paragraph._p.append(omath_el)


def add_inline_math(paragraph: Paragraph, latex: str) -> None:
    try:
        import latex2mathml.converter

        mathml = latex2mathml.converter.convert(latex)
        omath = _mathml_to_omml(mathml)
        if omath is not None:
            _insert_omml(paragraph, omath)
            return
    except Exception as exc:  # noqa: BLE001
        print(f"warning: math render failed: {exc}", file=sys.stderr)
    run = paragraph.add_run(latex)
    run.font.name = "Consolas"


def add_block_math(paragraph: Paragraph, latex: str) -> None:
    omath_para = OxmlElement("m:oMathPara")
    omath_para.set(qn("xmlns:m"), MATH_NS)
    try:
        import latex2mathml.converter

        mathml = latex2mathml.converter.convert(latex)
        omath = _mathml_to_omml(mathml)
        if omath is not None:
            omath_para.append(omath)
            paragraph._p.append(omath_para)
            return
    except Exception as exc:  # noqa: BLE001
        print(f"warning: math block render failed: {exc}", file=sys.stderr)
    run = paragraph.add_run(latex)
    run.font.name = "Consolas"
