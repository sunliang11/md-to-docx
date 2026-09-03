"""Preset definitions."""

from __future__ import annotations

from dataclasses import dataclass

from md_to_docx.paths import preset_template


@dataclass(frozen=True)
class Preset:
    name: str
    template: str | None
    toc: bool
    numbering: bool
    figure_label: str = "Figure"
    table_label: str = "Table"
    toc_title: str = "Contents"


PRESETS: dict[str, Preset] = {
    "professional": Preset(
        "professional", "professional", toc=True, numbering=False
    ),
    "editorial": Preset(
        "editorial", "editorial", toc=True, numbering=False,
        toc_title="Table of Contents",
    ),
    "technical": Preset(
        "technical", "technical", toc=True, numbering=True
    ),
    "academic": Preset(
        "academic", "academic", toc=True, numbering=True,
        figure_label="Figure", toc_title="Contents",
    ),
    "business": Preset(
        "business", "business", toc=False, numbering=False
    ),
    "report": Preset(
        "report", "report", toc=True, numbering=False
    ),
}


def load_preset(name: str) -> Preset:
    key = name.lower()
    if key not in PRESETS:
        valid = ", ".join(sorted(PRESETS))
        raise ValueError(f"unknown preset '{name}'\nhint: {valid}")
    return PRESETS[key]


def preset_template_path(preset: Preset):
    if preset.template is None:
        return None
    path = preset_template(preset.template)
    if not path.is_file():
        raise FileNotFoundError(f"template not found: {path}")
    return path
