"""Tests for CLI functionality."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def test_version_flag():
    """Test --version flag displays version."""
    result = subprocess.run(
        [sys.executable, "-m", "md_to_docx", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr


def test_help_flag():
    """Test --help flag displays help."""
    result = subprocess.run(
        [sys.executable, "-m", "md_to_docx", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "usage:" in output.lower() or "Usage:" in output


def test_missing_path_argument():
    """Test that missing path argument shows error."""
    result = subprocess.run(
        [sys.executable, "-m", "md_to_docx"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_sample_conversion(tmp_path: Path):
    """Test converting the sample fixture."""
    import shutil
    
    # Copy sample to temp dir
    sample_src = Path(__file__).parent / "fixtures" / "sample.md"
    sample_dst = tmp_path / "sample.md"
    shutil.copy(sample_src, sample_dst)
    
    # Convert it
    result = subprocess.run(
        [sys.executable, "-m", "md_to_docx", str(sample_dst)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    # Should succeed
    assert result.returncode == 0, f"Conversion failed: {result.stderr}"
    
    # Output docx should exist
    output_docx = sample_dst.with_suffix(".docx")
    assert output_docx.exists(), "Output .docx not created"
    assert output_docx.stat().st_size > 1000, "Output .docx too small"
