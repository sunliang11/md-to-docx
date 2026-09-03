"""Command-line interface for md-to-docx."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from md_to_docx import __version__
from md_to_docx.converter import collect_md_files, convert_file
from md_to_docx.diff.ast_diff import diff_documents, format_diff
from md_to_docx.load import load_document
from md_to_docx.paths import native_reference_doc
from md_to_docx.preset import PRESETS, load_preset, preset_template_path
from md_to_docx.reverse import reverse_docx
from md_to_docx.validate import validate_file

SUBCOMMANDS = frozenset({"convert", "reverse", "diff", "build", "mcp"})


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


def _add_convert_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, nargs="?", help="Markdown file or directory")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATTERN")
    parser.add_argument("--output-dir", type=Path, default=None, metavar="DIR")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
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
        choices=sorted(PRESETS),
        default=None,
    )
    parser.add_argument("--check", action="store_true", help="Validate without converting")
    parser.add_argument("--check-format", choices=["text", "json"], default="text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors (--check)")
    parser.add_argument(
        "--plugin",
        action="append",
        default=[],
        metavar="PATH",
        help="Load a transform plugin (can be repeated)",
    )
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="Disable built-in plugins (mermaid, math, captions)",
    )


def build_convert_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="The open-source document compiler — Markdown / AI output to professional DOCX.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    _add_convert_args(parser)
    return parser


def build_reverse_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert DOCX to Markdown.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", type=Path, help="Input .docx file")
    parser.add_argument("-o", "--output", type=Path, required=True, metavar="PATH")
    return parser


def build_diff_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diff two documents (.md or .docx).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("a", type=Path, help="First document")
    parser.add_argument("b", type=Path, help="Second document")
    parser.add_argument(
        "--format",
        choices=["text", "json", "md"],
        default="text",
        dest="diff_format",
    )
    return parser


def build_build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rebuild bundled Word template assets (developer / release use).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "target",
        choices=["presets", "all"],
        help="presets / all: rebuild preset + native reference templates",
    )
    return parser


def _apply_preset(args: argparse.Namespace) -> None:
    if not getattr(args, "preset", None):
        return
    try:
        preset = load_preset(args.preset)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
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


def _run_check(args: argparse.Namespace) -> int:
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


def _run_convert(args: argparse.Namespace) -> int:
    if args.check:
        return _run_check(args)

    if not args.path:
        build_convert_parser().error("the following arguments are required: path")

    _apply_preset(args)
    if args.toc is None:
        args.toc = False
    if args.template is None:
        args.template = native_reference_doc()

    plugin_paths = tuple(args.plugin)
    no_plugins = args.no_plugins

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
            print(f"would convert: {md} -> {out_docx}")
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
                plugin_paths=plugin_paths,
                no_plugins=no_plugins,
            )
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"fail: {md}: {exc}", file=sys.stderr)

    total = len(planned)
    print(f"done: {total - failures}/{total} succeeded")
    return 1 if failures else 0


def _run_reverse(args: argparse.Namespace) -> int:
    docx_path = args.input.resolve()
    out_path = args.output.resolve()
    if not docx_path.is_file():
        print(f"error: file not found: {docx_path}", file=sys.stderr)
        return 2
    try:
        reverse_docx(docx_path, out_path)
        print(f"ok: {docx_path} -> {out_path}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _run_diff(args: argparse.Namespace) -> int:
    path_a = args.a.resolve()
    path_b = args.b.resolve()
    for p in (path_a, path_b):
        if not p.is_file():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2
    try:
        doc_a = load_document(path_a)
        doc_b = load_document(path_b)
        changes = diff_documents(doc_a, doc_b)
        print(format_diff(changes, fmt=args.diff_format), end="")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _run_build(args: argparse.Namespace) -> int:
    from md_to_docx import presets_build

    try:
        if args.target in ("presets", "all"):
            presets_build.main()
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]

    if args_list and args_list[0] in SUBCOMMANDS:
        command = args_list[0]
        rest = args_list[1:]
        if command == "convert":
            return _run_convert(build_convert_parser().parse_args(rest))
        if command == "reverse":
            return _run_reverse(build_reverse_parser().parse_args(rest))
        if command == "diff":
            return _run_diff(build_diff_parser().parse_args(rest))
        if command == "build":
            return _run_build(build_build_parser().parse_args(rest))
        if command == "mcp":
            from md_to_docx.mcp.server import main as mcp_main

            return mcp_main(rest)

    return _run_convert(build_convert_parser().parse_args(args_list))
