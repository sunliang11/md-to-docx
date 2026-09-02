"""Mermaid CLI wrapper."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from md_to_docx.util.browser import find_browser_executable


def render_mermaid_to_files(
    source: str,
    out_svg: Path,
    *,
    png: Path | None = None,
    scale: float | None = None,
    browser: str | None = None,
) -> None:
    mmdc = shutil.which("mmdc")
    if not mmdc:
        raise RuntimeError("`mmdc` not found on PATH")

    scale = scale if scale is not None else float(os.environ.get("MD_TO_DOCX_MERMAID_SCALE", "4"))
    browser = browser or find_browser_executable()

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "diagram.mmd"
        src.write_text(source, encoding="utf-8")
        cfg = Path(tmp) / "puppeteer.json"
        if browser:
            cfg.write_text(json.dumps({"executablePath": browser}), encoding="utf-8")

        out_svg.parent.mkdir(parents=True, exist_ok=True)
        cmd = [mmdc, "-i", str(src), "-o", str(out_svg), "-b", "white", "-s", str(scale)]
        if cfg.exists():
            cmd.extend(["-p", str(cfg)])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr or result.stdout or "mmdc failed")

        if png is not None:
            cmd_png = [mmdc, "-i", str(src), "-o", str(png), "-b", "white", "-s", str(scale)]
            if cfg.exists():
                cmd_png.extend(["-p", str(cfg)])
            result2 = subprocess.run(cmd_png, capture_output=True, text=True)
            if result2.returncode != 0:
                raise RuntimeError(result2.stderr or "mmdc png failed")
