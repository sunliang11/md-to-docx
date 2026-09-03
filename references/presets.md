# Presets

Presets bundle a template and default flags. Explicit CLI flags override preset defaults.

| Preset | TOC | Numbering | Use case |
|--------|-----|-----------|----------|
| `professional` | yes | no | General documents |
| `editorial` | yes | no | Editorial (Georgia/KaiTi, wide margins) |
| `technical` | yes | yes | Technical reports, API docs |
| `academic` | yes | yes | Papers (Times/SimSun) |
| `business` | no | no | Business summaries |
| `report` | yes | no | Meeting notes, reports |

## Examples

```bash
./bin/convert report.md --preset technical
./bin/convert report.md --preset professional --no-toc
```

## Rebuild preset templates

```bash
md-to-docx build presets
# or: python -m md_to_docx.presets_build
```

Templates are written to `assets/presets/` and bundled into the wheel.

## Custom templates

Pass any `.docx` whose styles and header/footer you want to reuse:

```bash
./bin/convert report.md --template my-letterhead.docx
```

See [assets/templates/README.md](../assets/templates/README.md).
