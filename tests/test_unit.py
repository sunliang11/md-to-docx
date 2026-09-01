"""Unit tests for converter functions."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from md_to_docx.converter import (
    MERMAID_BLOCK_RE,
    collect_md_files,
    mermaid_images_dir,
    resolve_mermaid_scale,
    resolve_mermaid_width,
)


class TestMermaidRegex:
    """Tests for mermaid block regex matching."""

    def test_mermaid_block_matches(self):
        text = """
# Title

```mermaid
graph TD
    A --> B
```

More text.
"""
        matches = list(MERMAID_BLOCK_RE.finditer(text))
        assert len(matches) == 1
        assert "graph TD" in matches[0].group(1)
        assert "A --> B" in matches[0].group(1)

    def test_mermaid_block_case_insensitive(self):
        text = """```MeRmAiD
graph LR
    X --> Y
```"""
        matches = list(MERMAID_BLOCK_RE.finditer(text))
        assert len(matches) == 1

    def test_no_mermaid_block(self):
        text = """
```python
print("hello")
```
"""
        matches = list(MERMAID_BLOCK_RE.finditer(text))
        assert len(matches) == 0

    def test_multiple_mermaid_blocks(self):
        text = """
```mermaid
graph TD
    A
```

```mermaid
sequenceDiagram
    Alice->>Bob: Hi
```
"""
        matches = list(MERMAID_BLOCK_RE.finditer(text))
        assert len(matches) == 2


class TestMermaidImagesDir:
    """Tests for mermaid PNG output directory naming."""

    def test_mermaid_images_dir_name(self, tmp_path: Path):
        md_file = tmp_path / "LogCollectV2架构说明.md"
        assert mermaid_images_dir(md_file) == tmp_path / "LogCollectV2架构说明mermaid图片"

    def test_mermaid_images_dir_simple_stem(self, tmp_path: Path):
        md_file = tmp_path / "foo.md"
        assert mermaid_images_dir(md_file) == tmp_path / "foomermaid图片"


class TestCollectMdFiles:
    """Tests for collect_md_files function."""

    def test_collect_single_file(self, tmp_path: Path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")
        
        result = collect_md_files(md_file)
        assert len(result) == 1
        assert result[0].name == "test.md"

    def test_collect_directory(self, tmp_path: Path):
        (tmp_path / "file1.md").write_text("# File 1")
        (tmp_path / "file2.md").write_text("# File 2")
        (tmp_path / "other.txt").write_text("Not markdown")
        
        result = collect_md_files(tmp_path)
        assert len(result) == 2
        assert all(f.suffix == ".md" for f in result)

    def test_collect_nested_directories(self, tmp_path: Path):
        (tmp_path / "top.md").write_text("# Top")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.md").write_text("# Nested")
        
        result = collect_md_files(tmp_path)
        assert len(result) == 2
        names = {f.name for f in result}
        assert names == {"top.md", "nested.md"}

    def test_collect_excludes_dot_git(self, tmp_path: Path):
        (tmp_path / "normal.md").write_text("# Normal")
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config.md").write_text("# Git config")
        
        result = collect_md_files(tmp_path)
        # Should collect both currently (exclusion is a TODO in CLI safety)
        # This test documents current behavior
        names = {f.name for f in result}
        assert "normal.md" in names

    def test_non_markdown_file_raises(self, tmp_path: Path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Not markdown")
        
        with pytest.raises(SystemExit):
            collect_md_files(txt_file)

    def test_nonexistent_path_raises(self, tmp_path: Path):
        fake_path = tmp_path / "nonexistent.md"
        
        with pytest.raises(SystemExit):
            collect_md_files(fake_path)


class TestEnvParsing:
    """Tests for environment variable parsing."""

    def test_default_mermaid_scale(self, monkeypatch):
        monkeypatch.delenv("MD_TO_DOCX_MERMAID_SCALE", raising=False)
        assert resolve_mermaid_scale() == 4.0

    def test_custom_mermaid_scale(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_SCALE", "5.5")
        assert resolve_mermaid_scale() == 5.5

    def test_invalid_mermaid_scale_falls_back(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_SCALE", "not-a-number")
        assert resolve_mermaid_scale() == 4.0

    def test_negative_mermaid_scale_falls_back(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_SCALE", "-1")
        assert resolve_mermaid_scale() == 4.0

    def test_zero_mermaid_scale_falls_back(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_SCALE", "0")
        assert resolve_mermaid_scale() == 4.0

    def test_default_mermaid_width(self, monkeypatch):
        monkeypatch.delenv("MD_TO_DOCX_MERMAID_WIDTH", raising=False)
        assert resolve_mermaid_width() is None

    def test_custom_mermaid_width(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_WIDTH", "1200")
        assert resolve_mermaid_width() == 1200

    def test_invalid_mermaid_width_returns_none(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_WIDTH", "invalid")
        assert resolve_mermaid_width() is None

    def test_negative_mermaid_width_returns_none(self, monkeypatch):
        monkeypatch.setenv("MD_TO_DOCX_MERMAID_WIDTH", "-100")
        assert resolve_mermaid_width() is None
