"""Tests for CLI functionality."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "md_to_docx", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_version_flag():
    """Test --version flag displays version."""
    result = run_cli("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_help_flag():
    """Test --help flag displays help."""
    result = run_cli("--help")
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "usage:" in output.lower() or "Usage:" in output
    assert "--dry-run" in output
    assert "--output-dir" in output


def test_missing_path_argument():
    """Test that missing path argument shows error."""
    result = run_cli()
    assert result.returncode != 0


def test_dry_run_lists_files_without_writing(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "content.md").write_text("# Content")

    result = run_cli("--dry-run", str(tmp_path))
    assert result.returncode == 0
    assert "would convert" in result.stdout
    assert "content.md" in result.stdout
    assert "README.md" not in result.stdout
    assert not list(tmp_path.glob("*.docx"))


def test_output_dir_preserves_relative_paths(tmp_path: Path):
    sample_src = Path(__file__).parent / "fixtures" / "sample.md"
    docs = tmp_path / "docs"
    sub = docs / "nested"
    sub.mkdir(parents=True)
    shutil.copy(sample_src, sub / "sample.md")
    out_dir = tmp_path / "output"

    result = run_cli(str(docs), "--output-dir", str(out_dir))
    assert result.returncode == 0, result.stderr

    output_docx = out_dir / "nested" / "sample.docx"
    assert output_docx.exists()
    assert output_docx.stat().st_size > 1000
    assert not (sub / "sample.md").with_suffix(".docx").exists()


def test_skip_existing_skips_conversion(tmp_path: Path):
    sample_src = Path(__file__).parent / "fixtures" / "sample.md"
    sample_dst = tmp_path / "sample.md"
    shutil.copy(sample_src, sample_dst)
    existing = sample_dst.with_suffix(".docx")
    existing.write_text("placeholder")

    result = run_cli(str(sample_dst), "--skip-existing")
    assert result.returncode == 0
    assert "skip:" in result.stdout
    assert existing.read_text() == "placeholder"


def test_exclude_pattern(tmp_path: Path):
    (tmp_path / "keep.md").write_text("# Keep")
    (tmp_path / "skip.md").write_text("# Skip")

    result = run_cli(
        str(tmp_path),
        "--exclude",
        "skip.md",
        "--dry-run",
    )
    assert result.returncode == 0
    assert "keep.md" in result.stdout
    assert "skip.md" not in result.stdout


def test_sample_conversion(tmp_path: Path):
    """Test converting the sample fixture."""
    sample_src = Path(__file__).parent / "fixtures" / "sample.md"
    sample_dst = tmp_path / "sample.md"
    shutil.copy(sample_src, sample_dst)

    result = run_cli(str(sample_dst))
    assert result.returncode == 0, f"Conversion failed: {result.stderr}"

    output_docx = sample_dst.with_suffix(".docx")
    assert output_docx.exists(), "Output .docx not created"
    assert output_docx.stat().st_size > 1000, "Output .docx too small"
