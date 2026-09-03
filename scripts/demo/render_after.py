#!/usr/bin/env python3
"""Render a pseudo-Word preview image for demo assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "demo" / "after.png"
WIDTH = 900
MARGIN = 48
PAGE_BG = "#f3f4f6"
PAPER = "#ffffff"
INK = "#111827"
MUTED = "#4b5563"
CODE_BG = "#1f2937"
CODE_FG = "#e5e7eb"
BORDER = "#d1d5db"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> None:
    height = 720
    img = Image.new("RGB", (WIDTH, height), PAGE_BG)
    draw = ImageDraw.Draw(img)
    paper = (MARGIN, MARGIN, WIDTH - MARGIN, height - MARGIN)
    draw.rectangle(paper, fill=PAPER, outline=BORDER, width=1)

    x = MARGIN + 36
    y = MARGIN + 36
    title_font = _font(32, bold=True)
    h2_font = _font(22, bold=True)
    body_font = _font(15)
    small_font = _font(13)
    code_font = _font(13)

    draw.text((x, y), "Technical Report", fill=INK, font=title_font)
    y += 52
    draw.text((x, y), "Architecture", fill=INK, font=h2_font)
    y += 40
    draw.text(
        (x, y),
        "The document compiler transforms Markdown into professional Word files.",
        fill=MUTED,
        font=body_font,
    )
    y += 28
    draw.text(
        (x, y),
        "本编译器支持中英文混排，表格和代码块保持统一风格。",
        fill=MUTED,
        font=body_font,
    )
    y += 44

    # Table
    cols = ["Stage", "Input", "Output"]
    rows = [
        ["Normalize", "Raw .md", "Cleaned .md"],
        ["Native AST", "Document AST", ".docx"],
        ["Verify", ".docx", "SHA256 check"],
    ]
    col_widths = [140, 160, 160]
    row_h = 28
    table_w = sum(col_widths) + 2
    draw.rectangle((x, y, x + table_w, y + row_h * (len(rows) + 1)), outline=BORDER)
    cx = x
    for i, header in enumerate(cols):
        draw.rectangle((cx, y, cx + col_widths[i], y + row_h), fill="#f9fafb", outline=BORDER)
        draw.text((cx + 8, y + 6), header, fill=INK, font=small_font)
        cx += col_widths[i]
    y += row_h
    for row in rows:
        cx = x
        for i, cell in enumerate(row):
            draw.rectangle((cx, y, cx + col_widths[i], y + row_h), outline=BORDER)
            draw.text((cx + 8, y + 6), cell, fill=MUTED, font=small_font)
            cx += col_widths[i]
        y += row_h
    y += 24

    # Code block
    code_lines = [
        "./bin/convert input.md \\",
        "  --preset technical \\",
        "  --toc --numbering",
    ]
    code_h = len(code_lines) * 20 + 20
    draw.rectangle((x, y, x + 480, y + code_h), fill=CODE_BG)
    cy = y + 10
    for line in code_lines:
        draw.text((x + 12, cy), line, fill=CODE_FG, font=code_font)
        cy += 20

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
