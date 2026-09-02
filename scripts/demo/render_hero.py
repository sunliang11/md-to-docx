#!/usr/bin/env python3
"""Generate placeholder hero.gif with pseudo-terminal frames (Pillow)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "demo" / "hero.gif"
WIDTH = 800
HEIGHT = 400
BG = "#0d1117"
FG = "#c9d1d9"
GREEN = "#3fb950"
BLUE = "#58a6ff"
FRAME_MS = 1200


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


def _frame(lines: list[tuple[str, str]]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    font = _mono(16)
    y = 24
    for text, color in lines:
        draw.text((24, y), text, fill=color, font=font)
        y += 24
    return img


def main() -> None:
    frames = [
        _frame([
            ("$ ./bin/convert examples/technical-report/example.md", FG),
            ("", FG),
            ("Converting examples/technical-report/example.md ...", FG),
        ]),
        _frame([
            ("$ ./bin/convert examples/technical-report/example.md", FG),
            ("", FG),
            ("Converting examples/technical-report/example.md ...", FG),
            ("done: 1/1 succeeded", GREEN),
        ]),
        _frame([
            ("$ ./bin/convert examples/technical-report/example.md", FG),
            ("", FG),
            ("Converting examples/technical-report/example.md ...", FG),
            ("done: 1/1 succeeded", GREEN),
            ("", FG),
            ("→ examples/technical-report/example.docx", BLUE),
        ]),
        _frame([
            ("$ ./bin/convert examples/technical-report/example.md", FG),
            ("", FG),
            ("done: 1/1 succeeded", GREEN),
            ("→ examples/technical-report/example.docx", BLUE),
            ("", FG),
            ("Professional Word document ready.", GREEN),
        ]),
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=False,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
