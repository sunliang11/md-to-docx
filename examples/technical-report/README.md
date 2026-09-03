# Technical Report

What this example shows.

A systems design document with headings, tables, code blocks, a static architecture diagram, and mixed Chinese/English text. Demonstrates native conversion without requiring Mermaid CLI.

Mermaid fences are supported by the converter when `mmdc` is installed. This example uses a static PNG so the example builds anywhere with Python dependencies only.

## Convert

```bash
./bin/convert examples/technical-report/example.md --preset technical
```

Output: `examples/technical-report/example.docx`
