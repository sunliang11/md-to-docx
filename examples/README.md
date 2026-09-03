# Examples

These examples are converted with the native engine and presets.

## Gallery

| Example | Description | Convert |
|---------|-------------|---------|
| [Technical Report](technical-report/) | Systems design with tables, code, architecture diagram | `./bin/convert examples/technical-report/example.md` |
| [Business Report](business-report/) | Quarterly review with KPI tables and blockquotes | `./bin/convert examples/business-report/example.md` |
| [Academic Paper](academic-paper/) | Short paper with abstract, numbered sections, references | `./bin/convert examples/academic-paper/example.md` |
| [API Document](api-document/) | HTTP API reference with JSON/HTTP code blocks | `./bin/convert examples/api-document/example.md` |
| [Meeting Notes](meeting-notes/) | Sprint planning with task checklists and decisions | `./bin/convert examples/meeting-notes/example.md` |
| [AI Report](ai-report/) | AI-generated technical proposal (Overview / Design / Risks) | `./bin/convert examples/ai-report/example.md` |
| [Chinese Report](chinese-report/) | Pure Chinese technical proposal with numbered sections | `./bin/convert examples/chinese-report/example.md` |

## Rebuild all examples

```bash
bash scripts/demo/build_examples.sh
bash scripts/demo/render_previews.py
```

Each example directory contains:

- `example.md` — source Markdown
- `example.docx` — compiled output (committed to git)
- `preview.png` — first-page preview placeholder
- `README.md` — what the example demonstrates

## Requirements

- **Python 3.10+** — required for all examples
- **mmdc** — not required for these examples (technical-report uses a static PNG)
