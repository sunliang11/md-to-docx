# Templates

Place custom `.docx` reference files here for documentation, or pass any path via `--template`.

A good template includes:

- Normal / Heading 1–6 styles with your fonts
- Optional header and footer
- Page margins

The native renderer respects existing styles in the template and only adds `MDCodeBlock` / `Caption` if missing.

Rebuild built-in presets:

```bash
python -m md_to_docx.presets_build
```
