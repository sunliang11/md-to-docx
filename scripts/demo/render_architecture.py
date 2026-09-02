#!/usr/bin/env python3
"""Render architecture.png for technical-report example (static diagram)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "examples" / "technical-report" / "architecture.png"
WIDTH = 720
HEIGHT = 200


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _box(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, label: str, font) -> None:
    draw.rectangle((x, y, x + w, y + h), fill="#f9fafb", outline="#111827", width=2)
    tw = font.getlength(label)
    draw.text((x + (w - tw) / 2, y + (h - 16) / 2), label, fill="#111827", font=font)


def main() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(img)
    font = _font(14, bold=True)
    bw, bh = 120, 48
    y = 76
    boxes = [("Markdown", 40), ("Normalize", 200), ("Pandoc", 360), ("DOCX", 520)]
    for i, (label, x) in enumerate(boxes):
        _box(draw, x, y, bw, bh, label, font)
        if i < len(boxes) - 1:
            ax = x + bw + 4
            bx = boxes[i + 1][1] - 4
            mid = y + bh // 2
            draw.line([(ax, mid), (bx, mid)], fill="#111827", width=2)
            draw.polygon([(bx, mid), (bx - 8, mid - 5), (bx - 8, mid + 5)], fill="#111827")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
