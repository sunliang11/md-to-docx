#!/usr/bin/env python3
"""Render before.md.png from technical-report example.md (first 30 lines)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "examples" / "technical-report" / "example.md"
OUT = ROOT / "assets" / "demo" / "before.md.png"
WIDTH = 900
PADDING = 24
BG = "#1e1e1e"
FG = "#d4d4d4"
ACCENT = "#569cd6"
COMMENT = "#6a9955"


def _mono(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _color_line(line: str) -> str:
    s = line.strip()
    if s.startswith("#"):
        return ACCENT
    if s.startswith(">"):
        return COMMENT
    if s.startswith("|") or s.startswith("```"):
        return "#ce9178"
    return FG


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()[:30]
    font = _mono(14)
    line_h = 20
    height = PADDING * 2 + len(lines) * line_h + 20
    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)
    y = PADDING
    for i, line in enumerate(lines, 1):
        draw.text((PADDING, y), f"{i:3} ", fill="#858585", font=font)
        draw.text((PADDING + 36, y), line[:100], fill=_color_line(line), font=font)
        y += line_h
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
