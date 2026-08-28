"""Resolve bundled package data paths."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator


def data_dir() -> Path:
    """Writable package data directory (source tree in editable installs)."""
    return Path(__file__).resolve().parent / "data"


def bundled_resource(name: str):
    """Return a traversable handle to a bundled data file."""
    return files("md_to_docx.data").joinpath(name)


@contextmanager
def bundled_path(name: str) -> Iterator[Path]:
    """Yield a filesystem path to a bundled data file.

    Works for editable installs and wheel installs (extracts to temp when needed).
    """
    with as_file(bundled_resource(name)) as path:
        yield Path(path)


@contextmanager
def bundled_conversion_assets() -> Iterator[tuple[Path, Path]]:
    """Yield (reference_docx, lua_filter) paths for pandoc."""
    with bundled_path("reference-wecom.docx") as ref, bundled_path(
        "wecom-layout.lua"
    ) as lua:
        yield ref, lua
