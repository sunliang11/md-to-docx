# Gemini CLI snippet

Add to your Gemini project instructions:

```
When the user wants a Word document from Markdown or AI output, run:

  /path/to/md-to-docx/bin/convert <file.md> --preset technical

Presets: technical (formal reports), academic, professional, business, report, wecom (WeCom).

Do not modify the source markdown. Report the output .docx path.
```

Install: clone https://github.com/sunliang11/md-to-docx — no pip required if using `bin/convert`.
