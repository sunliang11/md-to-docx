"""Word field helpers (TOC, PAGE)."""

from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph


def _field_run(parent, instr: str, placeholder: str) -> None:
  p = parent._p
  r_begin = OxmlElement("w:r")
  fld_begin = OxmlElement("w:fldChar")
  fld_begin.set(qn("w:fldCharType"), "begin")
  r_begin.append(fld_begin)
  p.append(r_begin)

  r_instr = OxmlElement("w:r")
  instr_text = OxmlElement("w:instrText")
  instr_text.set(qn("xml:space"), "preserve")
  instr_text.text = instr
  r_instr.append(instr_text)
  p.append(r_instr)

  r_sep = OxmlElement("w:r")
  fld_sep = OxmlElement("w:fldChar")
  fld_sep.set(qn("w:fldCharType"), "separate")
  r_sep.append(fld_sep)
  p.append(r_sep)

  r_text = OxmlElement("w:r")
  t = OxmlElement("w:t")
  t.text = placeholder
  r_text.append(t)
  p.append(r_text)

  r_end = OxmlElement("w:r")
  fld_end = OxmlElement("w:fldChar")
  fld_end.set(qn("w:fldCharType"), "end")
  r_end.append(fld_end)
  p.append(r_end)


def add_toc_field(paragraph: Paragraph) -> None:
    _field_run(paragraph, r'TOC \o "1-3" \h \z \u', "Table of Contents")


def add_page_field(paragraph: Paragraph) -> None:
    _field_run(paragraph, "PAGE", "1")
