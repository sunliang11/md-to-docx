# Presets

Presets bundle a template, engine, and default flags. Explicit CLI flags override preset defaults.

| Preset | Engine | TOC | Numbering | Use case |
|--------|--------|-----|-----------|----------|
| `professional` | native | yes | no | General documents |
| `editorial` | native | yes | no | Editorial (Georgia/KaiTi, wide margins) |
| `technical` | native | yes | yes | Technical reports, API docs |
| `academic` | native | yes | yes | Papers (Times/SimSun) |
| `business` | native | no | no | Business summaries |
| `report` | native | yes | no | Meeting notes, reports |
| `wecom` | pandoc | no | no | 企业微信智能文档导入 |

## Examples

```bash
./bin/convert report.md --preset technical
./bin/convert report.md --preset wecom
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
