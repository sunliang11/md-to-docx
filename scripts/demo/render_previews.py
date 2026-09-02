#!/usr/bin/env python3
"""Generate preview.png for each example from H1 and first two paragraphs."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
WIDTH = 800
PADDING = 40
BG = "#ffffff"
INK = "#111827"
MUTED = "#6b7280"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _parse(md_text: str) -> tuple[str, list[str]]:
    lines = md_text.splitlines()
    title = ""
    paragraphs: list[str] = []
    in_para = False
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not title and stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("```"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            in_para = False
            continue
        if stripped.startswith("|") or stripped.startswith("- [") or stripped.startswith(">"):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if stripped:
            current.append(stripped)
            in_para = True
        elif in_para and current:
            paragraphs.append(" ".join(current))
            current = []
            in_para = False

    if current:
        paragraphs.append(" ".join(current))

    return title or "Example", paragraphs[:2]


def _wrap(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def render_preview(example_dir: Path) -> None:
    md_path = example_dir / "example.md"
    if not md_path.exists():
        return
    title, paragraphs = _parse(md_path.read_text(encoding="utf-8"))
    title_font = _font(28, bold=True)
    body_font = _font(16)
    max_text = WIDTH - 2 * PADDING

    wrapped_title = _wrap(title, title_font, max_text)
    wrapped_body: list[str] = []
    for para in paragraphs:
        wrapped_body.extend(_wrap(para, body_font, max_text))
        wrapped_body.append("")

    line_height_title = 36
    line_height_body = 24
    height = PADDING * 2 + len(wrapped_title) * line_height_title + 20
    height += len(wrapped_body) * line_height_body + 40

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    y = PADDING
    for line in wrapped_title:
        draw.text((PADDING, y), line, fill=INK, font=title_font)
        y += line_height_title
    y += 12
    draw.line([(PADDING, y), (WIDTH - PADDING, y)], fill="#e5e7eb", width=1)
    y += 16
    for line in wrapped_body:
        if line:
            draw.text((PADDING, y), line, fill=MUTED, font=body_font)
        y += line_height_body

    out = example_dir / "preview.png"
    img.save(out)
    print(f"Wrote {out}")


def main() -> None:
    for d in sorted(EXAMPLES.iterdir()):
        if d.is_dir() and (d / "example.md").exists():
            render_preview(d)


if __name__ == "__main__":
    main()
