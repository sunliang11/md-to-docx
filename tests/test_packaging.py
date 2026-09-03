"""Smoke checks for bundled preset assets (including wheel force-includes)."""

from __future__ import annotations

from md_to_docx.preset import PRESETS, load_preset, preset_template_path


def test_all_presets_have_bundled_templates():
    for name in PRESETS:
        preset = load_preset(name)
        path = preset_template_path(preset)
        assert path is not None
        assert path.is_file(), f"missing template for preset {name}: {path}"
        assert path.stat().st_size > 1000


def test_editorial_template_resolves():
    path = preset_template_path(load_preset("editorial"))
    assert path is not None
    assert path.name == "editorial.docx"
    assert path.is_file()
