# md-to-docx

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Batch-convert Markdown to DOCX for **WeCom (企业微信) smart-document import** —「导入本地文档」.

Tables, nested lists, heading hierarchy, and embedded images survive better than pasting raw Markdown into WeCom.

---

## English

### Overview

Pipeline:

```
.md → normalize spacing → mermaid → PNG (optional) → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

1. **Preprocess** — normalize blank lines around headings, tables, code blocks, horizontal rules, images
2. **Mermaid** — render ` ```mermaid ` blocks to PNG beside the source file
3. **Pandoc** — GFM input, WeCom-style reference doc, Lua layout filter, 150 DPI images

### Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| [pandoc](https://pandoc.org/) 3.x | Always | Lua filter support recommended |
| [@mermaid-js/mermaid-cli](https://github.com/mermaid-js/mermaid-cli) (`mmdc`) | When `.md` contains mermaid blocks | `npm install -g @mermaid-js/mermaid-cli` |
| Chrome / Edge / Chromium | For mmdc | Auto-detected; override with `MD_TO_DOCX_BROWSER` |
| python-docx | Only to rebuild reference template | `pip install python-docx` |

```bash
# macOS example
brew install pandoc
npm install -g @mermaid-js/mermaid-cli
```

### Install

```bash
pip install md-to-docx
# or from source (development)
git clone https://github.com/<your-user>/md-to-docx.git
cd md-to-docx
pip install -e ".[dev]"
```

### Usage

```bash
md-to-docx <path>
# or
python3 -m md_to_docx <path>
```

- `<path>` is a `.md` file → convert that file only
- `<path>` is a directory → recursively convert all `*.md` under it

**Behavior**

1. Original `.md` files are **never modified**
2. Output `.docx` is written next to each source file (`foo.md` → `foo.docx`)
3. Mermaid blocks become PNGs in the same directory (`foo_mermaid_01.png`, …)
4. Per-file failures are reported; remaining files still convert

**Import to WeCom (manual)**

WeCom PC → 智能文档 → ・・・ → **导入本地文档** → select each `.docx`.

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | Mermaid PNG render scale |
| `MD_TO_DOCX_MERMAID_WIDTH` | _(unset)_ | Optional mmdc `-w` width in pixels |
| `MD_TO_DOCX_BROWSER` | auto-detect | Browser executable for mmdc |
| `PUPPETEER_EXECUTABLE_PATH` | auto-detect | Same as above |

```bash
MD_TO_DOCX_MERMAID_SCALE=5 md-to-docx ./docs
```

### Rebuild reference template

```bash
pip install python-docx
md-to-docx-build-reference
```

Regenerates `src/md_to_docx/data/reference-wecom.docx` with WeCom-like Word styles.

### Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

The Cursor skill at `~/.cursor/skills/md_to_docx` is a symlink to this repository — edit here, not in `.cursor/skills`.

---

## 中文

### 简介

将 Markdown 批量转换为 DOCX，用于**企业微信智能文档**的「导入本地文档」功能。

相比直接粘贴 Markdown，表格、嵌套列表、标题层级和嵌入图片的保留效果更好。

### 前置依赖

| 工具 | 是否必需 | 说明 |
|------|----------|------|
| [pandoc](https://pandoc.org/) 3.x | 必需 | 建议支持 Lua 过滤器 |
| [@mermaid-js/mermaid-cli](https://github.com/mermaid-js/mermaid-cli)（`mmdc`） | 含 mermaid 代码块时必需 | `npm install -g @mermaid-js/mermaid-cli` |
| Chrome / Edge / Chromium | mmdc 渲染用 | 自动检测；可用 `MD_TO_DOCX_BROWSER` 覆盖 |
| python-docx | 仅重建参考模板时需要 | `pip install python-docx` |

### 安装

```bash
pip install md-to-docx
# 或从源码安装（开发）
git clone https://github.com/<your-user>/md-to-docx.git
cd md-to-docx
pip install -e ".[dev]"
```

### 使用

```bash
md-to-docx <路径>
# 或
python3 -m md_to_docx <路径>
```

- 传入 `.md` 文件 → 仅转换该文件
- 传入目录 → 递归转换目录下所有 `*.md`

**行为说明**

1. 原始 `.md` **不会被修改**
2. 输出的 `.docx` 与源文件同目录（`foo.md` → `foo.docx`）
3. Mermaid 图渲染为同目录 PNG（`foo_mermaid_01.png` 等）
4. 单文件失败不影响其他文件；有失败时退出码非零

**导入企微（手动）**

企微 PC 端 → 智能文档 → ・・・ → **导入本地文档** → 选择生成的 `.docx`。

### 环境变量

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | Mermaid PNG 渲染倍率 |
| `MD_TO_DOCX_MERMAID_WIDTH` | 未设置 | mmdc `-w` 宽度（像素） |
| `MD_TO_DOCX_BROWSER` | 自动检测 | mmdc 使用的浏览器路径 |
| `PUPPETEER_EXECUTABLE_PATH` | 自动检测 | 同上 |

### 重建 Word 参考模板

```bash
pip install python-docx
md-to-docx-build-reference
```

### 开发说明

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Cursor skill 目录 `~/.cursor/skills/md_to_docx` 是指向本仓库的软链接，请在此仓库内迭代，无需复制到 `.cursor/skills`。

---

## License

MIT — see [LICENSE](LICENSE).
