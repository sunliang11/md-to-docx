"""Plugin loader."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from md_to_docx.plugin.base import Plugin, PluginBase
from md_to_docx.plugin.builtin import BUILTIN_PLUGINS


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"md_to_docx_plugin_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load plugin from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _instantiate_from_module(module) -> Plugin:
    if hasattr(module, "plugin"):
        obj = module.plugin
        if isinstance(obj, type) and issubclass(obj, PluginBase):
            return obj()
        if isinstance(obj, PluginBase):
            return obj
    for attr in dir(module):
        if attr.startswith("_"):
            continue
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, PluginBase) and obj is not PluginBase:
            return obj()
    raise ValueError(f"no Plugin instance found in {module.__file__}")


def load_plugins(
    *,
    extra_paths: tuple[str | Path, ...] = (),
    use_builtin: bool = True,
) -> list[Plugin]:
    plugins: list[Plugin] = []
    if use_builtin:
        for cls in BUILTIN_PLUGINS:
            plugins.append(cls())
    for raw in extra_paths:
        path = Path(raw).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"plugin not found: {path}")
        module = _load_module(path)
        plugins.append(_instantiate_from_module(module))
    return plugins
