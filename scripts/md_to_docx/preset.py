"""Preset definitions."""

from __future__ import annotations

from dataclasses import dataclass

from md_to_docx.paths import preset_template


@dataclass(frozen=True)
class Preset:
    name: str
    template: str | None
    engine: str
    toc: bool
    numbering: bool
    figure_label: str = "Figure"
    table_label: str = "Table"
    toc_title: str = "Contents"


PRESETS: dict[str, Preset] = {
    "professional": Preset(
        "professional", "professional", "native", toc=True, numbering=False
    ),
    "technical": Preset(
        "technical", "technical", "native", toc=True, numbering=True
    ),
    "academic": Preset(
        "academic", "academic", "native", toc=True, numbering=True,
        figure_label="Figure", toc_title="Contents",
    ),
    "business": Preset(
        "business", "business", "native", toc=False, numbering=False
    ),
    "report": Preset(
        "report", "report", "native", toc=True, numbering=False
    ),
    "wecom": Preset(
        "wecom", None, "pandoc", toc=False, numbering=False
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
