"""Resolve bundled package data paths."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator


def _repo_root() -> Path:
    """Repository root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent.parent


def assets_dir() -> Path:
    """Canonical assets directory.

    In a source checkout, assets live at ``<repo>/assets/``.
    In a wheel install, they are bundled under ``md_to_docx/data/``.
    """
    repo_assets = _repo_root() / "assets"
    if repo_assets.is_dir():
        return repo_assets
    wheel_data = Path(__file__).resolve().parent / "data"
    if wheel_data.is_dir():
        return wheel_data
    return repo_assets


def data_dir() -> Path:
    """Writable directory for generated reference templates."""
    return assets_dir()


def _resolve_asset_path(name: str) -> Path | None:
    repo_asset = _repo_root() / "assets" / name
    if repo_asset.is_file():
        return repo_asset
    wheel_asset = Path(__file__).resolve().parent / "data" / name
    if wheel_asset.is_file():
        return wheel_asset
    return None


def bundled_resource(name: str):
    """Return a traversable handle to a bundled data file."""
    resolved = _resolve_asset_path(name)
    if resolved is not None:
        return resolved
    return files("md_to_docx.data").joinpath(name)


@contextmanager
def bundled_path(name: str) -> Iterator[Path]:
    """Yield a filesystem path to a bundled data file.

    Works for editable installs (repo ``assets/``), wheel installs
    (``md_to_docx/data/``), and importlib temp extraction when needed.
    """
    resolved = _resolve_asset_path(name)
    if resolved is not None:
        yield resolved
        return
    with as_file(files("md_to_docx.data").joinpath(name)) as path:
        yield Path(path)


def native_reference_doc() -> Path:
    """Path to built-in native reference template."""
    path = _resolve_asset_path("reference-native.docx")
    if path is not None:
        return path
    out = assets_dir() / "reference-native.docx"
    if not out.is_file():
        from md_to_docx.reference_native import build_native_reference

        build_native_reference(out.parent)
    return out


def preset_template(name: str) -> Path:
    path = _resolve_asset_path(f"presets/{name}.docx")
    if path is not None:
        return path
    return assets_dir() / "presets" / f"{name}.docx"
