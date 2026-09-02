# Community Templates

Contribute Word templates for md-to-docx. This directory is the **marketplace** until a static site (Gate B) ships.

## Directory layout

Each template lives in its own subdirectory:

```
templates/
  my-template/
    template.docx   # Word reference file (required)
    sample.md       # Example Markdown (required)
    preview.png     # Screenshot or preview image (required)
    LICENSE         # Must allow redistribution (required)
```

## Naming

- Use lowercase kebab-case: `technical-design`, `consulting-report`
- Avoid trademarked names (e.g. use `consulting-report`, not `mckinsey-like`)

## PR checklist

Before submitting a template PR, confirm:

- [ ] `template.docx` opens cleanly in Microsoft Word
- [ ] CJK text renders with appropriate fonts (e.g. Microsoft YaHei, SimSun)
- [ ] No macros, no embedded personal information
- [ ] `sample.md` converts successfully:

  ```bash
  md-to-docx templates/my-template/sample.md \
    --template templates/my-template/template.docx \
    --output-dir /tmp/out
  ```

- [ ] `LICENSE` permits redistribution (MIT recommended)
- [ ] `preview.png` included (screenshot or generated preview)

## Usage

```bash
md-to-docx report.md --template templates/technical-design/template.docx
```

## Built-in templates

| Directory | Style |
|-----------|-------|
| `technical-design/` | Technical documentation |
| `consulting-report/` | Business / consulting report |
| `academic-ieee-ish/` | Academic / conference paper |
| `chinese-official/` | Chinese official document style |

See [ODM spec](../spec/document-markdown.md) for supported Markdown syntax.
