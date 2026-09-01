"""Command-line interface for md-to-docx."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from md_to_docx import __version__
from md_to_docx.converter import (
    DEFAULT_MERMAID_SCALE,
    MERMAID_BACKGROUND,
    MERMAID_BLOCK_RE,
    collect_md_files,
    convert_one,
    ensure_bundled_assets,
    find_browser_executable,
    require_cmd,
    resolve_mermaid_scale,
    resolve_mermaid_width,
    write_puppeteer_config,
)
from md_to_docx.paths import bundled_conversion_assets


def resolve_output_docx(
    md_path: Path,
    output_dir: Path | None,
    scan_root: Path | None,
) -> Path:
    """Map a source .md path to its destination .docx path."""
    if output_dir is None:
        return md_path.with_suffix(".docx")
    if scan_root is not None:
        try:
            rel = md_path.relative_to(scan_root)
            return output_dir / rel.with_suffix(".docx")
        except ValueError:
            pass
    return output_dir / f"{md_path.stem}.docx"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to DOCX (pandoc + optional mermaid-cli).",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Markdown file or directory (directories are scanned recursively)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Exclude files matching pattern (can be used multiple times)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Write .docx files to a specific directory",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip conversion if output .docx already exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be converted without converting them",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = args.path.resolve()
    is_directory = input_path.is_dir()
    scan_root = input_path if is_directory else None
    exclude_patterns = tuple(args.exclude)

    md_files = collect_md_files(
        input_path,
        exclude_patterns=exclude_patterns,
        apply_default_excludes=is_directory,
    )
    if not md_files:
        print("no .md files found")
        return 0

    output_dir = args.output_dir.resolve() if args.output_dir else None
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    planned: list[tuple[Path, Path]] = []
    for md in md_files:
        out_docx = resolve_output_docx(md, output_dir, scan_root)
        if args.skip_existing and out_docx.is_file():
            print(f"skip: {md} (exists: {out_docx})")
            continue
        planned.append((md, out_docx))

    if args.dry_run:
        for md, out_docx in planned:
            print(f"would convert: {md} -> {out_docx}")
        print(f"dry-run: {len(planned)} file(s)")
        return 0

    if not planned:
        print("no files to convert")
        return 0

    ensure_bundled_assets()

    pandoc = require_cmd("pandoc")
    mmdc = shutil.which("mmdc")

    needs_mmdc = False
    for md, _ in planned:
        try:
            sample = md.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {md}: {exc}", file=sys.stderr)
            continue
        if MERMAID_BLOCK_RE.search(sample):
            needs_mmdc = True
            break
    if needs_mmdc and not mmdc:
        print(
            "error: one or more files contain mermaid blocks but `mmdc` not found. "
            "Install @mermaid-js/mermaid-cli (npm i -g @mermaid-js/mermaid-cli).",
            file=sys.stderr,
        )
        return 1

    browser = find_browser_executable() if needs_mmdc else None
    scale = resolve_mermaid_scale() if needs_mmdc else DEFAULT_MERMAID_SCALE
    mermaid_width = resolve_mermaid_width() if needs_mmdc else None
    if needs_mmdc and browser:
        print(f"mermaid browser: {browser}")
    if needs_mmdc:
        print(f"mermaid scale: {scale}")
        if mermaid_width is not None:
            print(f"mermaid width: {mermaid_width}")
        print(f"mermaid background: {MERMAID_BACKGROUND}")

    failures = 0
    with tempfile.TemporaryDirectory(prefix="md_to_docx_cfg_") as cfg_dir:
        puppeteer_config: Path | None = None
        if needs_mmdc:
            puppeteer_config = Path(cfg_dir) / "puppeteer.json"
            write_puppeteer_config(puppeteer_config, browser)

        with bundled_conversion_assets() as (reference_doc, lua_filter):
            for md, out_docx in planned:
                try:
                    convert_one(
                        md,
                        pandoc,
                        reference_doc,
                        lua_filter,
                        mmdc,
                        puppeteer_config,
                        scale,
                        mermaid_width,
                        out_docx=out_docx,
                    )
                except Exception as exc:  # noqa: BLE001 — per-file isolation
                    failures += 1
                    print(f"fail: {md}: {exc}", file=sys.stderr)

    total = len(planned)
    print(f"done: {total - failures}/{total} succeeded")
    return 1 if failures else 0
