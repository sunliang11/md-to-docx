"""MCP stdio server entry."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from md_to_docx import __version__
from md_to_docx.mcp.handlers import (
    handle_apply_template,
    handle_convert_markdown,
    handle_list_presets,
    handle_validate_document,
)

TOOL_HANDLERS = {
    "convert_markdown": handle_convert_markdown,
    "apply_template": handle_apply_template,
    "validate_document": handle_validate_document,
    "list_presets": handle_list_presets,
}

TOOL_SCHEMAS = [
    {
        "name": "convert_markdown",
        "description": (
            "Convert Markdown to a local DOCX file. "
            "Provide input_path (file path) or markdown (string). "
            "Returns output_path on disk."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string", "description": "Path to .md file"},
                "markdown": {"type": "string", "description": "Markdown content"},
                "output_path": {"type": "string", "description": "Output .docx path"},
                "preset": {
                    "type": "string",
                    "description": "Preset name (technical, academic, etc.)",
                },
                "template": {"type": "string", "description": "Custom template .docx path"},
                "toc": {"type": "boolean", "description": "Include table of contents"},
            },
        },
    },
    {
        "name": "apply_template",
        "description": "Convert with a specific template file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "template": {"type": "string"},
                "output_path": {"type": "string"},
            },
            "required": ["input_path", "template", "output_path"],
        },
    },
    {
        "name": "validate_document",
        "description": "Validate markdown without converting to DOCX.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "markdown": {"type": "string"},
                "strict": {"type": "boolean"},
            },
        },
    },
    {
        "name": "list_presets",
        "description": "List available document presets.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _print_help() -> None:
    print("md-to-docx MCP server")
    print(f"version: {__version__}")
    print("tools: convert_markdown, apply_template, validate_document, list_presets")
    print("preview: not in 2.0 — see web playground")
    print("Run without --help to start stdio transport.")


async def _run_server() -> None:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    server = Server("md-to-docx")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=schema["name"],
                description=schema["description"],
                inputSchema=schema["inputSchema"],
            )
            for schema in TOOL_SCHEMAS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            result = {"ok": False, "problem": f"unknown tool: {name}"}
        else:
            result = handler(arguments or {})
        import json

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--help" in args or "-h" in args:
        _print_help()
        return 0
    if "--version" in args:
        print(__version__)
        return 0
    asyncio.run(_run_server())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
