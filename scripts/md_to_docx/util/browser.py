"""Browser discovery for mmdc."""

from __future__ import annotations

import os
from pathlib import Path

_BROWSER_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
)


def find_browser_executable() -> str | None:
    env = os.environ.get("MD_TO_DOCX_BROWSER") or os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if env and Path(env).is_file():
        return env
    for candidate in _BROWSER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None
