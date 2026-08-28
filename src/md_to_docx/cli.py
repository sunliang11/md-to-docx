"""CLI entry point for md-to-docx."""

from __future__ import annotations

import sys

from md_to_docx.converter import main as convert_main


def main(argv: list[str] | None = None) -> int:
    return convert_main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
