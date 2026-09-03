# GitHub Action — md-to-docx

Compile Markdown to professional DOCX in CI. Markdown stays in Git; DOCX is a build artifact.

## Usage

```yaml
name: Build DOCX

on:
  push:
    branches: [main]
  pull_request:

jobs:
  docx:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: sunliang11/md-to-docx/action@v3
        with:
          input: docs/report.md
          preset: technical
          output-dir: dist/docx

      - uses: actions/upload-artifact@v4
        with:
          name: docx
          path: dist/docx
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `input` | yes | — | Markdown file or directory |
| `preset` | no | `technical` | Template preset |
| `output-dir` | no | `dist/docx` | Output directory |

## Local testing

From the repository root:

```yaml
- uses: ./action
  with:
    input: examples/meeting-notes/example.md
    preset: technical
```

## Git workflow recommendation

- Keep `.md` files in version control as the source of truth
- Add `dist/docx/` or `*.docx` to `.gitignore` (optional)
- Build DOCX in CI and publish as artifacts or releases
