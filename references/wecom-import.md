# WeCom import guide

## Manual import steps

WeCom does not support automated upload from this tool. After conversion:

1. Open **企业微信** on PC
2. Go to **智能文档**
3. Click **・・・** (more menu)
4. Select **导入本地文档**
5. Choose the generated `.docx` file(s)

Repeat for each document. Output files sit beside the source Markdown (`foo.md` → `foo.docx`).

## Acceptance checklist

After converting a sample document, verify:

1. **Layout** — H2/H3/H4 hierarchy is visible; blockquotes, code blocks, and body text have consistent spacing
2. **Tables** — bordered with readable header row; wide tables (>6 columns) use smaller compact font
3. **Images** — Mermaid diagrams and local screenshots are sharp enough at normal zoom
4. **Source safety** — original `.md` files are unchanged

## Format expectations

- Local images in Markdown are embedded into DOCX at 150 DPI; WeCom re-uploads them on import
- Mermaid must be pre-rendered to PNG or pandoc emits raw code fences
- For local screenshots, source width ≥1200px gives best results; the converter does not resample
- Very wide tables may still look tight in WeCom (compact style mitigates but cannot fully fix)
- Inline `` `code` `` and some Word styles may flatten after WeCom import — structure (headings, lists, tables) is preserved best

## Mermaid PNG files

Mermaid blocks become PNGs under `{stem}mermaid图片/` beside the source file (e.g. `foomermaid图片/foo_mermaid_01.png`). These are referenced in a temporary copy used only during conversion; originals are not modified.
