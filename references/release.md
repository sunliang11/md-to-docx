# Release checklist

Do not tag until all items pass.

1. `pip install -e ".[dev]" && pytest tests/ -v` — all green
2. `bash scripts/demo/build_examples.sh` — 7 example docx regenerated
3. `python -m md_to_docx.presets_build` — templates committed
4. `CHANGELOG.md` — `[1.0.0]` dated
5. User runs (when ready):

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions `release.yml` will run tests, build wheel/sdist, and attach to the Release.

PyPI upload is optional and manual (`twine upload`); package name: `md2docx-compiler`.
