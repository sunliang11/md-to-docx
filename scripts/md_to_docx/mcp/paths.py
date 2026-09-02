"""Path jail for MCP output paths."""

from __future__ import annotations

import os
from pathlib import Path

from md_to_docx.errors import path_jail_violation


def _allowed_roots(
  input_path: Path | None,
  cwd: Path | None = None,
) -> list[Path]:
  roots: list[Path] = []
  base_cwd = (cwd or Path.cwd()).resolve()
  roots.append(base_cwd)

  if input_path is not None:
    roots.append(input_path.resolve().parent)

  env_out = os.environ.get("MD_TO_DOCX_OUT")
  if env_out:
    out = Path(env_out).expanduser().resolve()
    roots.append(out)

  return roots


def _is_under(path: Path, root: Path) -> bool:
  try:
    path.relative_to(root)
    return True
  except ValueError:
    return False


def validate_output_path(
  output_path: Path,
  *,
  input_path: Path | None = None,
  cwd: Path | None = None,
) -> Path:
  resolved = output_path.expanduser().resolve()
  roots = _allowed_roots(input_path, cwd=cwd)
  for root in roots:
    if _is_under(resolved, root):
      return resolved
  raise path_jail_violation(str(output_path))
