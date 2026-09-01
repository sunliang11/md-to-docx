"""Convert Markdown to DOCX via pandoc; Mermaid blocks → PNG first.

Original .md files are never modified. Outputs (.docx, mermaid PNGs) land
beside each source file. Directory paths are processed recursively.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from md_to_docx.normalizer import normalize_markdown_content
from md_to_docx.paths import assets_dir, bundled_conversion_assets, bundled_path

MERMAID_BLOCK_RE = re.compile(
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL | re.IGNORECASE,
)
FENCED_CODE_RE = re.compile(r"^```", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|.+\|\s*$", re.MULTILINE)
TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|\s*$", re.MULTILINE)
HR_RE = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$", re.MULTILINE)
IMAGE_RE = re.compile(r"^!\[.*\]\(.*\)\s*$", re.MULTILINE)

DEFAULT_MERMAID_SCALE = 4.0
MERMAID_BACKGROUND = "white"

# Prefer system browsers so mmdc works without puppeteer's chrome-headless-shell.
_BROWSER_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
)


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def require_cmd(name: str) -> str:
    path = shutil.which(name)
    if not path:
        die(f"`{name}` not found on PATH. Install it before running this script.")
    return path


def collect_md_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".md":
            die(f"not a Markdown file: {path}")
        return [path.resolve()]
    if path.is_dir():
        return sorted(p.resolve() for p in path.rglob("*.md") if p.is_file())
    die(f"path does not exist: {path}")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_browser_executable() -> str | None:
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH") or os.environ.get(
        "MD_TO_DOCX_BROWSER"
    )
    if env and Path(env).is_file():
        return env
    for candidate in _BROWSER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None


def write_puppeteer_config(config_path: Path, executable: str | None) -> None:
    cfg: dict = {
        "args": ["--no-sandbox", "--disable-setuid-sandbox"],
    }
    if executable:
        cfg["executablePath"] = executable
    config_path.write_text(json.dumps(cfg), encoding="utf-8")


def resolve_mermaid_scale() -> float:
    raw = os.environ.get("MD_TO_DOCX_MERMAID_SCALE")
    if raw is None or raw.strip() == "":
        return DEFAULT_MERMAID_SCALE
    try:
        scale = float(raw)
    except ValueError:
        print(
            f"warning: invalid MD_TO_DOCX_MERMAID_SCALE={raw!r}; "
            f"using default {DEFAULT_MERMAID_SCALE}",
            file=sys.stderr,
        )
        return DEFAULT_MERMAID_SCALE
    if scale <= 0:
        print(
            f"warning: MD_TO_DOCX_MERMAID_SCALE must be > 0 (got {scale}); "
            f"using default {DEFAULT_MERMAID_SCALE}",
            file=sys.stderr,
        )
        return DEFAULT_MERMAID_SCALE
    return scale


def resolve_mermaid_width() -> int | None:
    raw = os.environ.get("MD_TO_DOCX_MERMAID_WIDTH")
    if raw is None or raw.strip() == "":
        return None
    try:
        width = int(raw)
    except ValueError:
        print(
            f"warning: invalid MD_TO_DOCX_MERMAID_WIDTH={raw!r}; ignoring",
            file=sys.stderr,
        )
        return None
    if width <= 0:
        print(
            f"warning: MD_TO_DOCX_MERMAID_WIDTH must be > 0 (got {width}); ignoring",
            file=sys.stderr,
        )
        return None
    return width


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
    """Fix Markdown content issues before pandoc (tables, lists, headings, etc.)."""
    return normalize_markdown_content(text)


def _normalize_layout(text: str) -> str:
    """Normalize spacing so pandoc produces cleaner DOCX layout."""
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
    """Content fixes plus pandoc-friendly structural spacing."""
    had_trailing_newline = text.endswith("\n")
    result = _normalize_layout(_normalize_content(text))
    if had_trailing_newline and not result.endswith("\n"):
        result += "\n"
    return result


def render_mermaid_blocks(
    source_md: Path,
    text: str,
    mmdc: str,
    puppeteer_config: Path | None,
    scale: float,
    width: int | None,
) -> tuple[str, list[Path]]:
    """Replace mermaid fences with image links; write PNGs next to source_md."""
    matches = list(MERMAID_BLOCK_RE.finditer(text))
    if not matches:
        return text, []

    out_dir = source_md.parent
    stem = source_md.stem
    png_paths: list[Path] = []
    pieces: list[str] = []
    last = 0

    for idx, match in enumerate(matches, start=1):
        pieces.append(text[last : match.start()])
        code = match.group(1).strip() + "\n"
        png_name = f"{stem}_mermaid_{idx:02d}.png"
        png_path = out_dir / png_name

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".mmd",
            encoding="utf-8",
            delete=False,
        ) as tmp:
            tmp.write(code)
            mmd_path = Path(tmp.name)

        try:
            cmd = [
                mmdc,
                "-i",
                str(mmd_path),
                "-o",
                str(png_path),
                "-b",
                MERMAID_BACKGROUND,
                "-s",
                str(scale),
            ]
            if width is not None:
                cmd.extend(["-w", str(width)])
            if puppeteer_config is not None:
                cmd.extend(["-p", str(puppeteer_config)])
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                err = (result.stderr or result.stdout or "").strip()
                raise RuntimeError(
                    f"mmdc failed for {source_md.name} block #{idx}: {err}"
                )
            if not png_path.is_file():
                raise RuntimeError(
                    f"mmdc reported success but PNG missing: {png_path}"
                )
        finally:
            mmd_path.unlink(missing_ok=True)

        png_paths.append(png_path)
        pieces.append(f"\n![{stem} mermaid {idx}]({png_name})\n")
        last = match.end()

    pieces.append(text[last:])
    return "".join(pieces), png_paths


def convert_one(
    md_path: Path,
    pandoc: str,
    reference_doc: Path,
    lua_filter: Path,
    mmdc: str | None,
    puppeteer_config: Path | None,
    scale: float,
    mermaid_width: int | None,
) -> None:
    if not reference_doc.is_file():
        die(
            f"reference doc missing: {reference_doc}. "
            "Run python3 -m md_to_docx.reference first."
        )
    if not lua_filter.is_file():
        die(f"lua filter missing: {lua_filter}")

    original_hash = file_sha256(md_path)
    text = normalize_md(md_path.read_text(encoding="utf-8"))
    has_mermaid = bool(MERMAID_BLOCK_RE.search(text))

    if has_mermaid:
        if not mmdc:
            raise RuntimeError(
                "file contains mermaid blocks but `mmdc` is not on PATH. "
                "Install @mermaid-js/mermaid-cli."
            )
        processed, _ = render_mermaid_blocks(
            md_path, text, mmdc, puppeteer_config, scale, mermaid_width
        )
    else:
        processed = text

    processed = normalize_md(processed)
    out_docx = md_path.with_suffix(".docx")

    # Temp md beside source so relative images (./img, mermaid PNGs) resolve.
    temp_md = md_path.parent / f".{md_path.stem}.__md_to_docx_tmp__.md"
    try:
        temp_md.write_text(processed, encoding="utf-8")
        cmd = [
            pandoc,
            str(temp_md),
            "-f",
            "gfm+yaml_metadata_block",
            "--reference-doc",
            str(reference_doc),
            "--lua-filter",
            str(lua_filter),
            "--dpi",
            "150",
            "--wrap",
            "preserve",
            "--resource-path",
            str(md_path.parent),
            "-o",
            str(out_docx),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"pandoc failed for {md_path}: {err}")
    finally:
        temp_md.unlink(missing_ok=True)

    if file_sha256(md_path) != original_hash:
        raise RuntimeError(f"source md was modified unexpectedly: {md_path}")

    print(f"ok: {md_path} -> {out_docx}")


def _try_build_reference_doc(output_dir: Path) -> bool:
    """Build reference-wecom.docx when missing. Returns True if file exists after."""
    try:
        from md_to_docx.reference import build_reference_doc
    except ImportError:
        die(
            "reference-wecom.docx is missing and python-docx is not installed. "
            "Either: pip install python-docx && "
            "PYTHONPATH=<skill-root>/scripts python3 -m md_to_docx.reference "
            "or restore assets/reference-wecom.docx from the repo."
        )
    try:
        build_reference_doc(output_dir)
    except Exception as exc:  # noqa: BLE001
        die(f"failed to build reference-wecom.docx: {exc}")
    return (output_dir / "reference-wecom.docx").is_file()


def ensure_bundled_assets() -> None:
    """Fail fast when package data is missing; auto-build reference doc if possible."""
    assets = assets_dir()
    ref_path = assets / "reference-wecom.docx"
    lua_path = assets / "wecom-layout.lua"

    if not ref_path.is_file():
        print(
            f"reference-wecom.docx missing at {ref_path}; building…",
            file=sys.stderr,
        )
        if not _try_build_reference_doc(assets):
            die(f"reference doc still missing after build: {ref_path}")

    if not lua_path.is_file():
        with bundled_path("wecom-layout.lua") as lua:
            if not lua.is_file():
                die(f"lua filter missing: {lua_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to DOCX (pandoc + optional mermaid-cli).",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Markdown file or directory (directories are scanned recursively)",
    )
    args = parser.parse_args(argv)

    ensure_bundled_assets()

    pandoc = require_cmd("pandoc")
    mmdc = shutil.which("mmdc")

    md_files = collect_md_files(args.path)
    if not md_files:
        print("no .md files found")
        return 0

    # Pre-check mmdc only if any file needs it
    needs_mmdc = False
    for md in md_files:
        try:
            sample = md.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"error: cannot read {md}: {exc}", file=sys.stderr)
            continue
        if MERMAID_BLOCK_RE.search(sample):
            needs_mmdc = True
            break
    if needs_mmdc and not mmdc:
        die(
            "one or more files contain mermaid blocks but `mmdc` not found. "
            "Install @mermaid-js/mermaid-cli (npm i -g @mermaid-js/mermaid-cli)."
        )

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
            for md in md_files:
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
                    )
                except Exception as exc:  # noqa: BLE001 — per-file isolation
                    failures += 1
                    print(f"fail: {md}: {exc}", file=sys.stderr)

    total = len(md_files)
    print(f"done: {total - failures}/{total} succeeded")
    return 1 if failures else 0
