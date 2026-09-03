"""Convert Markdown to DOCX (native Document AST).

Original .md files are never modified. Outputs (.docx, mermaid media) land
beside each source file. Directory paths are processed recursively.
"""

from __future__ import annotations

import fnmatch
import hashlib
import re
import sys
from pathlib import Path

from md_to_docx.normalizer import normalize_markdown_content

FENCED_CODE_RE = re.compile(r"^```", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|.+\|\s*$", re.MULTILINE)
TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|\s*$", re.MULTILINE)
HR_RE = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"^!\[.*\]\(.*\)\s*$", re.MULTILINE)

DEFAULT_EXCLUDE_PATTERNS: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "SKILL.md",
    ".github/**",
)
ALWAYS_SKIP_DIRS: frozenset[str] = frozenset({".git", "node_modules"})


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _matches_exclude_pattern(rel_posix: str, name: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return rel_posix == prefix or rel_posix.startswith(f"{prefix}/")
    return fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_posix, pattern)


def is_excluded(
    md_path: Path,
    base_dir: Path,
    patterns: tuple[str, ...],
) -> bool:
    rel = md_path.relative_to(base_dir)
    rel_posix = rel.as_posix()
    name = md_path.name
    return any(
        _matches_exclude_pattern(rel_posix, name, pattern) for pattern in patterns
    )


def _should_skip_path(md_path: Path, base_dir: Path) -> bool:
    rel_parts = md_path.relative_to(base_dir).parts
    return any(part in ALWAYS_SKIP_DIRS for part in rel_parts[:-1])


def collect_md_files(
    path: Path,
    *,
    exclude_patterns: tuple[str, ...] = (),
    apply_default_excludes: bool = False,
) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".md":
            die(f"not a Markdown file: {path}")
        return [path.resolve()]
    if path.is_dir():
        base = path.resolve()
        patterns = (
            DEFAULT_EXCLUDE_PATTERNS + exclude_patterns
            if apply_default_excludes
            else exclude_patterns
        )
        results: list[Path] = []
        for candidate in base.rglob("*.md"):
            if not candidate.is_file():
                continue
            if _should_skip_path(candidate, base):
                continue
            if patterns and is_excluded(candidate, base, patterns):
                continue
            results.append(candidate.resolve())
        return sorted(results)
    die(f"path does not exist: {path}")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_table_line(line: str) -> bool:
    return bool(TABLE_ROW_RE.match(line) or TABLE_SEP_RE.match(line))


def _table_block_range(lines: list[str], idx: int) -> tuple[int, int] | None:
    """Return (start, end_exclusive) if idx is inside a contiguous GFM table block."""
    if not _is_table_line(lines[idx]):
        return None
    start = idx
    while start > 0 and _is_table_line(lines[start - 1]):
        start -= 1
    end = idx + 1
    while end < len(lines) and _is_table_line(lines[end]):
        end += 1
    # Valid GFM table: header row + separator somewhere in first two lines
    if end - start >= 2:
        if TABLE_SEP_RE.match(lines[start + 1]) or (
            start + 2 < end and TABLE_SEP_RE.match(lines[start + 2])
        ):
            return start, end
    return None


def _is_in_fenced_code(lines: list[str], idx: int) -> bool:
    in_fence = False
    for i in range(idx):
        if FENCED_CODE_RE.match(lines[i].strip()):
            in_fence = not in_fence
    return in_fence


def _normalize_content(text: str) -> str:
    """Fix Markdown content issues before conversion (tables, lists, headings, etc.)."""
    return normalize_markdown_content(text)


def _normalize_layout(text: str) -> str:
    """Normalize spacing for cleaner DOCX layout."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Compress 3+ consecutive blank lines to 2.
    out_lines: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                out_lines.append("")
        else:
            blank_run = 0
            out_lines.append(line)

    n = len(out_lines)
    # Precompute table block ranges so we never split rows with blank lines.
    table_ranges: list[tuple[int, int]] = []
    i = 0
    while i < n:
        block = _table_block_range(out_lines, i)
        if block is None:
            i += 1
            continue
        start, end = block
        if not table_ranges or start >= table_ranges[-1][1]:
            table_ranges.append(block)
        i = end

    def in_table_block(line_idx: int) -> bool:
        for start, end in table_ranges:
            if start <= line_idx < end:
                return True
        return False

    # Ensure blank lines around structural blocks.
    result: list[str] = []
    for i, line in enumerate(out_lines):
        stripped = line.strip()
        prev = out_lines[i - 1].strip() if i > 0 else ""
        nxt = out_lines[i + 1].strip() if i + 1 < n else ""

        needs_blank_before = False
        needs_blank_after = False
        inside_table = in_table_block(i)

        if not _is_in_fenced_code(out_lines, i) and not inside_table:
            if HEADING_RE.match(line) and prev != "":
                needs_blank_before = True
            if HR_RE.match(stripped) and prev != "":
                needs_blank_before = True
            if IMAGE_RE.match(stripped) and prev != "":
                needs_blank_before = True
            if (
                table_ranges
                and any(i == start for start, _ in table_ranges)
                and prev != ""
            ):
                needs_blank_before = True
            if FENCED_CODE_RE.match(stripped) and prev != "":
                needs_blank_before = True

            if HEADING_RE.match(line) and nxt != "" and not FENCED_CODE_RE.match(nxt):
                needs_blank_after = True
            if HR_RE.match(stripped) and nxt != "":
                needs_blank_after = True
            if IMAGE_RE.match(stripped) and nxt != "":
                needs_blank_after = True
            if FENCED_CODE_RE.match(stripped) and nxt != "":
                needs_blank_after = True

        if needs_blank_before and (not result or result[-1].strip() != ""):
            result.append("")
        result.append(line)
        if needs_blank_after:
            result.append("")

    normalized = "\n".join(result)
    if text.endswith("\n") and not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def normalize_md(text: str) -> str:
    """Content fixes plus structural spacing for native conversion."""
    had_trailing_newline = text.endswith("\n")
    result = _normalize_layout(_normalize_content(text))
    if had_trailing_newline and not result.endswith("\n"):
        result += "\n"
    return result


def convert_file(
    md_path: Path,
    out_docx: Path,
    *,
    normalize: bool = True,
    template_path: Path | None = None,
    toc: bool = False,
    toc_title: str = "Contents",
    numbering: bool = False,
    title: str | None = None,
    author: str | None = None,
    date: str | None = None,
    doc_version: str | None = None,
    page_numbers: bool = True,
    strict_mermaid: bool = False,
    figure_label: str = "Figure",
    table_label: str = "Table",
    section_label: str = "Section",
    plugin_paths: tuple[str | Path, ...] = (),
    no_plugins: bool = False,
) -> None:
    """Convert a single markdown file with the native engine."""
    from md_to_docx.engine.native import NativeOptions, convert_native

    convert_native(
        md_path,
        out_docx,
        options=NativeOptions(
            normalize=normalize,
            template_path=template_path,
            toc=toc,
            toc_title=toc_title,
            numbering=numbering,
            title=title,
            author=author,
            date=date,
            doc_version=doc_version,
            page_numbers=page_numbers,
            strict_mermaid=strict_mermaid,
            figure_label=figure_label,
            table_label=table_label,
            section_label=section_label,
            plugin_paths=plugin_paths,
            no_plugins=no_plugins,
        ),
    )
