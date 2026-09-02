"""Pandoc engine wrapper."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from md_to_docx.converter import (
    DEFAULT_MERMAID_SCALE,
    MERMAID_BLOCK_RE,
    convert_one,
    ensure_bundled_assets,
    find_browser_executable,
    require_cmd,
    resolve_mermaid_scale,
    resolve_mermaid_width,
    write_puppeteer_config,
)
from md_to_docx.paths import bundled_conversion_assets


def convert_pandoc(md_path: Path, out_docx: Path) -> None:
    ensure_bundled_assets()
    pandoc = require_cmd("pandoc")
    mmdc = shutil.which("mmdc")
    text = md_path.read_text(encoding="utf-8")
    needs_mmdc = bool(MERMAID_BLOCK_RE.search(text))
    if needs_mmdc and not mmdc:
        raise RuntimeError("mermaid blocks present but mmdc not found")

    browser = find_browser_executable() if needs_mmdc else None
    scale = resolve_mermaid_scale() if needs_mmdc else DEFAULT_MERMAID_SCALE
    mermaid_width = resolve_mermaid_width() if needs_mmdc else None

    with tempfile.TemporaryDirectory(prefix="md_to_docx_cfg_") as cfg_dir:
        puppeteer_config = None
        if needs_mmdc:
            puppeteer_config = Path(cfg_dir) / "puppeteer.json"
            write_puppeteer_config(puppeteer_config, browser)
        with bundled_conversion_assets() as (reference_doc, lua_filter):
            convert_one(
                md_path,
                pandoc,
                reference_doc,
                lua_filter,
                mmdc,
                puppeteer_config,
                scale,
                mermaid_width,
                out_docx=out_docx,
            )
