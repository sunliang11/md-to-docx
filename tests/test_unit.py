"""Unit tests for converter functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from md_to_docx.converter import collect_md_files, is_excluded
from md_to_docx.util.mmdc import resolve_mermaid_scale, resolve_mermaid_width


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
        names = {f.name for f in result}
        assert names == {"normal.md"}

    def test_collect_excludes_node_modules(self, tmp_path: Path):
        (tmp_path / "normal.md").write_text("# Normal")
        node_dir = tmp_path / "node_modules" / "pkg"
        node_dir.mkdir(parents=True)
        (node_dir / "readme.md").write_text("# Package")

        result = collect_md_files(tmp_path)
        names = {f.name for f in result}
        assert names == {"normal.md"}

    def test_collect_default_excludes_readme(self, tmp_path: Path):
        (tmp_path / "README.md").write_text("# Readme")
        (tmp_path / "content.md").write_text("# Content")

        result = collect_md_files(tmp_path, apply_default_excludes=True)
        names = {f.name for f in result}
        assert names == {"content.md"}

    def test_collect_default_excludes_github_dir(self, tmp_path: Path):
        (tmp_path / "content.md").write_text("# Content")
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "workflow.md").write_text("# Workflow")

        result = collect_md_files(tmp_path, apply_default_excludes=True)
        names = {f.name for f in result}
        assert names == {"content.md"}

    def test_collect_single_file_ignores_default_excludes(self, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text("# Readme")

        result = collect_md_files(readme)
        assert len(result) == 1
        assert result[0].name == "README.md"

    def test_collect_custom_exclude_pattern(self, tmp_path: Path):
        (tmp_path / "draft.md").write_text("# Draft")
        (tmp_path / "final.md").write_text("# Final")

        result = collect_md_files(
            tmp_path,
            exclude_patterns=("draft.md",),
            apply_default_excludes=False,
        )
        names = {f.name for f in result}
        assert names == {"final.md"}

    def test_is_excluded_github_glob(self, tmp_path: Path):
        github_file = tmp_path / ".github" / "notes.md"
        github_file.parent.mkdir(parents=True)
        github_file.write_text("# Notes")

        assert is_excluded(github_file, tmp_path, (".github/**",))

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
    """Tests for Mermaid environment variable parsing."""

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
