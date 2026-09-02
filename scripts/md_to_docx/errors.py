"""Structured errors for API, MCP, and Web layers."""

from __future__ import annotations

DOCS_URL = "https://github.com/sunliang11/md-to-docx/blob/main/references/mcp.md"


class MdToDocxError(Exception):
    """User-facing error with problem / cause / fix."""

    def __init__(
        self,
        problem: str,
        cause: str,
        fix: str,
        *,
        docs: str = DOCS_URL,
    ) -> None:
        self.problem = problem
        self.cause = cause
        self.fix = fix
        self.docs = docs
        super().__init__(problem)

    def to_dict(self) -> dict[str, str]:
        return {
            "problem": self.problem,
            "cause": self.cause,
            "fix": self.fix,
            "docs": self.docs,
        }

    def __str__(self) -> str:
        return (
            f"problem: {self.problem}\n"
            f"cause: {self.cause}\n"
            f"fix: {self.fix}\n"
            f"docs: {self.docs}"
        )


def unknown_preset(name: str) -> MdToDocxError:
    return MdToDocxError(
        "Unknown preset",
        f"preset '{name}' is not defined",
        "Use list_presets or --preset professional|technical|academic|business|report|wecom",
    )


def missing_template(path: str) -> MdToDocxError:
    return MdToDocxError(
        "Template not found",
        f"template file missing: {path}",
        "Rebuild presets with python -m md_to_docx.presets_build or pass a valid --template path",
    )


def missing_pandoc() -> MdToDocxError:
    return MdToDocxError(
        "Pandoc not found",
        "engine=pandoc requires pandoc on PATH",
        "Install pandoc: brew install pandoc (macOS) or use engine=native",
    )


def missing_mmdc() -> MdToDocxError:
    return MdToDocxError(
        "Mermaid CLI not found",
        "document contains mermaid blocks but mmdc is not on PATH",
        "npm i -g @mermaid-js/mermaid-cli, remove mermaid blocks, or use engine=native without mermaid",
    )


def empty_document() -> MdToDocxError:
    return MdToDocxError(
        "Empty document",
        "markdown has no convertible content",
        "Add headings or body text before converting",
    )


def path_jail_violation(path: str) -> MdToDocxError:
    return MdToDocxError(
        "Output path not allowed",
        f"output_path '{path}' is outside allowed directories",
        "Write output under cwd, input parent directory, or MD_TO_DOCX_OUT",
    )


def missing_input() -> MdToDocxError:
    return MdToDocxError(
        "No input provided",
        "neither input_path nor markdown was supplied",
        "Provide input_path or markdown text",
    )


def conversion_failed(cause: str) -> MdToDocxError:
    return MdToDocxError(
        "Conversion failed",
        cause,
        "Check input markdown and engine options; see docs for troubleshooting",
    )
