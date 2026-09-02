"""Command-line interface for md-to-docx."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from md_to_docx import __version__
from md_to_docx.converter import collect_md_files, convert_file
from md_to_docx.paths import native_reference_doc
from md_to_docx.preset import load_preset, preset_template_path
from md_to_docx.validate import validate_file


def resolve_output_docx(
    md_path: Path,
    output_dir: Path | None,
    scan_root: Path | None,
) -> Path:
    if output_dir is None:
        return md_path.with_suffix(".docx")
    if scan_root is not None:
        try:
            rel = md_path.relative_to(scan_root)
            return output_dir / rel.with_suffix(".docx")
        except ValueError:
            pass
    return output_dir / f"{md_path.stem}.docx"


def resolve_engine(args: argparse.Namespace) -> str:
    if args.engine:
        return args.engine
    return os.environ.get("MD_TO_DOCX_ENGINE", "native")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="The open-source document compiler — Markdown / AI output to professional DOCX.",
    )
    parser.add_argument("path", type=Path, nargs="?", help="Markdown file or directory")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATTERN")
    parser.add_argument("--output-dir", type=Path, default=None, metavar="DIR")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--engine", choices=["native", "pandoc"], default=None)
    parser.add_argument("--normalize", dest="normalize", action="store_true", default=True)
    parser.add_argument("--no-normalize", dest="normalize", action="store_false")
    parser.add_argument("--template", type=Path, default=None, metavar="PATH")
    parser.add_argument("--toc", dest="toc", action="store_true", default=None)
    parser.add_argument("--no-toc", dest="toc", action="store_false")
    parser.add_argument("--toc-title", default="Contents")
    parser.add_argument("--title", default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--date", default=None)
    parser.add_argument("--doc-version", default=None)
    parser.add_argument("--no-page-numbers", action="store_true")
    parser.add_argument("--numbering", action="store_true")
    parser.add_argument("--strict-mermaid", action="store_true")
    parser.add_argument("--figure-label", default="Figure")
    parser.add_argument("--table-label", default="Table")
    parser.add_argument("--section-label", default="Section")
    parser.add_argument(
        "--preset",
        choices=["professional", "technical", "academic", "business", "report", "wecom"],
        default=None,
    )
    parser.add_argument("--check", action="store_true", help="Validate without converting")
    parser.add_argument("--check-format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors (--check)")
    return parser


def _apply_preset(args: argparse.Namespace) -> None:
    if not args.preset:
        return
    try:
        preset = load_preset(args.preset)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if preset.engine == "pandoc":
        args.engine = "pandoc"
        if args.template:
            print("warning: --template ignored for wecom/pandoc preset", file=sys.stderr)
    else:
        if args.engine is None:
            args.engine = preset.engine
        if args.toc is None:
            args.toc = preset.toc
        if not args.numbering:
            args.numbering = preset.numbering
        if args.template is None and preset.template:
            try:
                args.template = preset_template_path(preset)
            except FileNotFoundError as exc:
                print(f"error: {exc}", file=sys.stderr)
                raise SystemExit(2) from exc
        args.figure_label = preset.figure_label
        args.table_label = preset.table_label
        args.toc_title = preset.toc_title


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check:
        if not args.path:
            print("error: path required for --check", file=sys.stderr)
            return 2
        path = args.path.resolve()
        targets = [path] if path.is_file() else collect_md_files(path)
        all_issues = []
        for md in targets:
            all_issues.extend(validate_file(md, strict=args.strict))
        if args.check_format == "json":
            print(json.dumps([i.__dict__ for i in all_issues], indent=2))
        else:
            errors = warnings = 0
            for issue in all_issues:
                loc = f"{args.path}:{issue.line}: " if issue.line else f"{args.path}: "
                print(f"{loc}{issue.severity}: {issue.code}: {issue.message}")
                if issue.severity == "error":
                    errors += 1
                else:
                    warnings += 1
            print(f"summary: {errors} error(s), {warnings} warning(s)")
        return 1 if any(i.severity == "error" for i in all_issues) else 0

    if not args.path:
        parser.error("the following arguments are required: path")

    _apply_preset(args)
    engine = resolve_engine(args)
    if args.toc is None:
        args.toc = False
    if args.template is None and engine == "native":
        args.template = native_reference_doc()

    input_path = args.path.resolve()
    is_directory = input_path.is_dir()
    scan_root = input_path if is_directory else None
    md_files = collect_md_files(
        input_path,
        exclude_patterns=tuple(args.exclude),
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
            print(f"would convert: {md} -> {out_docx} [{engine}]")
        print(f"dry-run: {len(planned)} file(s)")
        return 0

    if not planned:
        print("no files to convert")
        return 0

    failures = 0
    for md, out_docx in planned:
        try:
            convert_file(
                md,
                out_docx,
                engine=engine,
                normalize=args.normalize,
                template_path=args.template,
                toc=args.toc,
                toc_title=args.toc_title,
                numbering=args.numbering,
                title=args.title,
                author=args.author,
                date=args.date,
                doc_version=args.doc_version,
                page_numbers=not args.no_page_numbers,
                strict_mermaid=args.strict_mermaid,
                figure_label=args.figure_label,
                table_label=args.table_label,
                section_label=args.section_label,
            )
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"fail: {md}: {exc}", file=sys.stderr)

    total = len(planned)
    print(f"done: {total - failures}/{total} succeeded")
    return 1 if failures else 0
