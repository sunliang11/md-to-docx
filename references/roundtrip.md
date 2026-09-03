# Roundtrip (DOCX ↔ Markdown)

md-to-docx v1.1+ supports **reverse** conversion: DOCX → Document AST → Markdown.

## Commands

```bash
# DOCX → Markdown (native AST parser)
md-to-docx reverse report.docx -o report.md

# Diff two documents (.md or .docx)
md-to-docx diff v1.md v2.md
md-to-docx diff old.docx new.docx --format json
md-to-docx diff a.md b.md --format md   # changelog style
```

## When to use reverse

- You received a `.docx` and want **Markdown as the source of truth** in Git
- You need to **edit in Markdown** after a Word round-trip
- CI builds DOCX from Markdown; reverse helps audit drift

## When to use diff

- Compare two report versions at **structure level** (headings, tables, code blocks)
- Generate a changelog between Markdown drafts
- Verify roundtrip fidelity after `md → docx → reverse → md`

## Support matrix

| Feature | Forward (MD→DOCX) | Reverse (DOCX→MD) |
|---------|-------------------|-------------------|
| Headings 1–6 | Yes | Yes |
| Bold / italic / strike / code | Yes | Yes |
| Links | Yes | Yes |
| GFM tables | Yes | Yes |
| Fenced code blocks | Yes | Yes |
| Blockquotes | Yes | Partial |
| Images | Yes | Yes (media → `{stem}-media/`) |
| Lists | Yes | Best-effort |
| Page breaks | Yes | Yes (`<!-- pagebreak -->`) |
| Footnotes | Yes | Partial |
| Math (LaTeX/OMML) | Yes | Best-effort (plain text fallback) |
| Mermaid | Yes (PNG) | As ` ```mermaid ` fence if detected |
| TOC field | Yes | Skipped (warning) |
| Figure captions | Yes | Partial |

## Not supported (v1.1)

These OOXML features are **skipped with a warning** — conversion does not crash:

- Text boxes
- SmartArt
- Track changes / revisions
- Macros
- Embedded Excel charts
- Complex drawing charts

Do not expect pixel-perfect roundtrip for arbitrary Word documents. The golden path is **native-generated DOCX** from this tool's forward conversion.

## Git workflow

Keep Markdown in Git; treat DOCX as a build artifact:

```gitignore
dist/docx/
*.docx
```

Build in CI with the [GitHub Action](../action/README.md):

```yaml
- uses: sunliang11/md-to-docx/action@v1.1.0
  with:
    input: docs/report.md
    preset: technical
```
