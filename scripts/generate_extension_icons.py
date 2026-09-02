#!/usr/bin/env python3
"""Generate extension PNG icons from branding colors."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "browser-extension" / "icons"
SIZES = (16, 48, 128)


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (9, 105, 218, 255))
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 6,
        fill=(255, 255, 255, 255),
    )
    text = "MD"
    font_size = max(size // 3, 8)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 1), text, fill=(9, 105, 218, 255), font=font)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        path = OUT / f"icon{size}.png"
        draw_icon(size).save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
