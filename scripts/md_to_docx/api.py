"""Python API for Skill, MCP, and Web layers."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from md_to_docx.converter import convert_file
from md_to_docx.errors import (
  conversion_failed,
  empty_document,
  missing_input,
  missing_mmdc,
  missing_template,
  unknown_preset,
)
from md_to_docx.parse.markdown import parse_markdown
from md_to_docx.paths import native_reference_doc
from md_to_docx.preset import load_preset, preset_template_path
from md_to_docx.validate import Issue, validate_document, validate_file


@dataclass
class ConvertResult:
  output_path: Path
  warnings: list[str]


@dataclass
class ConvertOptions:
  normalize: bool = True
  template: Path | None = None
  toc: bool | None = None
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


def apply_preset(
  preset_name: str | None,
  options: ConvertOptions,
) -> ConvertOptions:
  if not preset_name:
    return options
  try:
    preset = load_preset(preset_name)
  except ValueError:
    raise unknown_preset(preset_name) from None

  if options.toc is None:
    options.toc = preset.toc
  if not options.numbering:
    options.numbering = preset.numbering
  if options.template is None and preset.template:
    try:
      options.template = preset_template_path(preset)
    except FileNotFoundError as exc:
      raise missing_template(str(exc)) from exc
  options.figure_label = preset.figure_label
  options.table_label = preset.table_label
  options.toc_title = preset.toc_title
  return options


def _default_output_dir() -> Path:
  env = os.environ.get("MD_TO_DOCX_OUT")
  if env:
    path = Path(env).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
  return Path(tempfile.gettempdir())


def _collect_warnings(text: str, base_dir: Path) -> list[str]:
  doc = parse_markdown(text, source_path=base_dir / "input.md")
  issues = validate_document(doc, base_dir=base_dir)
  return [f"{i.code}: {i.message}" for i in issues if i.severity == "warning"]


def validate_markdown(
  text: str,
  *,
  base_dir: Path | None = None,
  strict: bool = False,
) -> list[Issue]:
  base = base_dir or Path(tempfile.gettempdir())
  doc = parse_markdown(text, source_path=base / "input.md")
  issues = validate_document(doc, base_dir=base)
  if strict:
    issues = [
      Issue("error", i.code, i.message, i.line)
      if i.severity == "warning"
      else i
      for i in issues
    ]
  return issues


def validate_path(path: Path, *, strict: bool = False) -> list[Issue]:
  return validate_file(path.resolve(), strict=strict)


def convert(
  source: str | Path | None = None,
  *,
  output: Path | None = None,
  preset: str | None = None,
  template: Path | None = None,
  toc: bool | None = None,
  numbering: bool | None = None,
  markdown_text: str | None = None,
  toc_title: str = "Contents",
  title: str | None = None,
  author: str | None = None,
  date: str | None = None,
  doc_version: str | None = None,
  page_numbers: bool = True,
  strict_mermaid: bool = False,
  figure_label: str = "Figure",
  table_label: str = "Table",
  section_label: str = "Section",
  normalize: bool = True,
) -> ConvertResult:
  """Convert markdown file or text to DOCX."""
  if markdown_text is None and source is None:
    raise missing_input()

  options = ConvertOptions(
    normalize=normalize,
    template=template,
    toc=toc,
    toc_title=toc_title,
    numbering=numbering or False,
    title=title,
    author=author,
    date=date,
    doc_version=doc_version,
    page_numbers=page_numbers,
    strict_mermaid=strict_mermaid,
    figure_label=figure_label,
    table_label=table_label,
    section_label=section_label,
  )
  options = apply_preset(preset, options)
  if options.toc is None:
    options.toc = False
  if options.template is None:
    options.template = native_reference_doc()

  temp_dir: tempfile.TemporaryDirectory[str] | None = None
  md_path: Path

  if markdown_text is not None:
    temp_dir = tempfile.TemporaryDirectory(prefix="md_to_docx_")
    work = Path(temp_dir.name)
    md_path = work / "document.md"
    md_path.write_text(markdown_text, encoding="utf-8")
    text_for_validate = markdown_text
    validate_base = work
    if output is None:
      out_dir = _default_output_dir()
      output = out_dir / "document.docx"
  else:
    md_path = Path(source).expanduser().resolve()
    if not md_path.is_file():
      raise conversion_failed(f"input file not found: {md_path}")
    text_for_validate = md_path.read_text(encoding="utf-8")
    validate_base = md_path.parent
    if output is None:
      output = md_path.with_suffix(".docx")

  output = output.expanduser().resolve()
  output.parent.mkdir(parents=True, exist_ok=True)

  if not text_for_validate.strip():
    raise empty_document()

  warnings = _collect_warnings(text_for_validate, validate_base)

  try:
    with contextlib.redirect_stdout(io.StringIO()):
      convert_file(
        md_path,
        output,
        normalize=options.normalize,
        template_path=options.template,
        toc=options.toc,
        toc_title=options.toc_title,
        numbering=options.numbering,
        title=options.title,
        author=options.author,
        date=options.date,
        doc_version=options.doc_version,
        page_numbers=options.page_numbers,
        strict_mermaid=options.strict_mermaid,
        figure_label=options.figure_label,
        table_label=options.table_label,
        section_label=options.section_label,
      )
  except RuntimeError as exc:
    msg = str(exc)
    if "mmdc" in msg.lower() or "mermaid" in msg.lower():
      raise missing_mmdc() from exc
    raise conversion_failed(msg) from exc
  except Exception as exc:
    raise conversion_failed(str(exc)) from exc
  finally:
    if temp_dir is not None:
      temp_dir.cleanup()

  if not output.is_file() or output.stat().st_size == 0:
    raise conversion_failed("output docx was not created")

  return ConvertResult(
    output_path=output,
    warnings=warnings,
  )
