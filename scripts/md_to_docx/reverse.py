"""Reverse conversion: DOCX → Markdown."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from md_to_docx.parse.docx import parse_docx
from md_to_docx.write.markdown import write_markdown


def reverse_docx(
    docx_path: Path,
    out_path: Path,
    *,
    engine: str = "native",
) -> None:
    """Convert DOCX to Markdown."""
    if engine == "pandoc":
        print("warning: using pandoc fallback for reverse", file=sys.stderr)
        result = subprocess.run(
            ["pandoc", str(docx_path), "-t", "markdown", "-o", str(out_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr or "pandoc reverse failed")
        return

    doc = parse_docx(docx_path)
    md = write_markdown(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
