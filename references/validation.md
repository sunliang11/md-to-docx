# Document Validation

Validate Markdown without generating a `.docx`:

```bash
./bin/convert --check report.md
./bin/convert --check report.md --format json
./bin/convert --check report.md --strict
```

## Rules

| Code | Severity | Description |
|------|----------|-------------|
| `empty_document` | error | No content blocks |
| `heading_skip` | warning | Heading level jumps (e.g. H1 → H4) |
| `missing_image` | error | Referenced image file not found |
| `unresolved_xref` | error | `[@fig:]` / `[@tbl:]` without target |
| `missing_mermaid_cli` | warning | Mermaid blocks but no `mmdc` |

Exit code: `0` if clean or warnings only; `1` if any error (`--strict` promotes warnings to errors).
