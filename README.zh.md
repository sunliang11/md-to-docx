[English](README.md) | 中文

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml/badge.svg)](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

# md-to-docx

<img src="assets/branding/wordmark.svg" alt="md-to-docx: MD → DOCX" width="320">

**AI 时代的开源文档编译器。**

把 Markdown 与 AI 生成内容编译成专业 Word — 支持正向、反向、对比与 CI 自动化。

[文档](references/installation.md) · [示例](examples/README.md) · [GitHub](https://github.com/sunliang11/md-to-docx)

![Markdown 转 DOCX 演示](assets/demo/hero.gif)

**转换前**（Markdown）→ **转换后**（Word）

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">

## 你能做什么

| 做什么 | 一句话 | 试试 |
|--------|--------|------|
| **正向编译** | 把 Markdown / AI 文稿变成可交付的 Word | `md-to-docx report.md --preset technical` |
| **反向还原** | Word 转回 Markdown，方便当 Git 源文件维护 | `md-to-docx reverse report.docx -o report.md` |
| **版本对比** | 按文档结构对比两版差异（支持 .md 和 .docx） | `md-to-docx diff v1.md v2.md --format md` |
| **文档校验** | 只检查 Markdown，不生成 docx | `md-to-docx report.md --check` |
| **自定义插件** | 用小型 Python 插件改写转换逻辑 | `md-to-docx report.md --plugin my_plugin.py` |
| **CI 自动化** | GitHub Actions 构建 DOCX，仓库里只留 .md | `uses: sunliang11/md-to-docx/action@v3` |
| **编辑器导出** | VS Code / Obsidian 右键一键导出 Word | [VS Code](editors/vscode/README.md) · [Obsidian](editors/obsidian/README.md) |
| **AI 接入** | Cursor / MCP / 浏览器 — 全本地，无需 API Key | [SKILL.md](SKILL.md) · [MCP](references/mcp.md) |

**处理流程：** Markdown / AI 输出 → Document AST → 专业 DOCX（亦可反向）。

## 选择使用方式

| 入口 | 一句话 | 文档 |
|------|--------|------|
| CLI | 完整命令行工具（`md-to-docx`） | 本 README |
| `bin/convert` | clone 后无需 `pip install` 即可运行 | — |
| Python API | 脚本调用 `from md_to_docx.api import convert` | [development.md](references/development.md) |
| Cursor Skill | Agent 自动选 preset 并转换 | [SKILL.md](SKILL.md) |
| Claude / Codex / Gemini | 各平台 Skill 副本 | [skills/](skills/) |
| MCP | 四个工具：convert、validate、apply_template、list_presets | [mcp.md](references/mcp.md) |
| Web Playground | 浏览器编辑并下载 DOCX（Docker） | [web/README.md](web/README.md) |
| 浏览器扩展 | 从 ChatGPT / Claude / Gemini 对话导出 Word | [browser-extension/README.md](browser-extension/README.md) |
| VS Code | 命令 `MD: Export to DOCX`，Markdown 右键菜单 | [editors/vscode/README.md](editors/vscode/README.md) |
| Obsidian | `Export to Professional Word`（仅桌面端） | [editors/obsidian/README.md](editors/obsidian/README.md) |
| GitHub Action | CI 从 Markdown 构建 DOCX | [action/README.md](action/README.md) |

## 快速开始

**方式 A — Git 克隆（推荐，无需 pip）**

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md --preset technical
```

**方式 B — Docker Playground（无需本机 Python）**

```bash
docker compose -f web/docker-compose.yml up --build
# 浏览器打开 http://localhost:8080
```

## 命令

```bash
md-to-docx report.md --preset technical                              # 正向编译（默认）
md-to-docx reverse report.docx -o report.md                           # DOCX → Markdown
md-to-docx diff draft-v1.md draft-v2.md --format md                  # 结构对比
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py   # 自定义插件
md-to-docx report.md --check                                         # 仅校验
```

子命令：`convert`（默认）、`reverse`、`diff`。仍支持旧写法 `md-to-docx file.md`。`reverse` 与 `diff` 均支持 `.docx` 输入。Pandoc 降级：`md-to-docx reverse file.docx -o out.md --engine pandoc`。

**批量与目录**

```bash
md-to-docx ./docs --output-dir ./output --exclude "README.md"
md-to-docx ./docs --dry-run
```

### CLI 选项（分组）

**正向编译**

- `--preset` — `professional` \| `technical` \| `academic` \| `business` \| `report` \| `wecom`
- `--template PATH` — 自定义 Word 模板（native 引擎）
- `--toc` / `--numbering` — 目录与章节编号
- `--title` / `--author` / `--date` / `--doc-version` — 文档元数据
- `--engine native|pandoc` — 或环境变量 `MD_TO_DOCX_ENGINE`
- `--output-dir` / `--exclude` / `--skip-existing` / `--dry-run`
- `--plugin PATH`（可多次）/ `--no-plugins`
- `--strict-mermaid` / `--no-normalize`

**校验**

- `--check` / `--check-format text|json` / `--strict`

**反向**

- `-o PATH` / `--engine native|pandoc`

**对比**

- `--format text|json|md`

目录扫描默认跳过 `.git`、`node_modules`；排除 `README.md`、`CHANGELOG.md`、`SKILL.md`、`.github/**`。

## 文档格式支持

- **Native AST 引擎** — 默认；多数场景无需 pandoc
- **结构** — 标题、列表、表格、代码、引用、图片、脚注、任务列表
- **CJK** — 微软雅黑 / 宋体模板
- **Mermaid** — 安装 `mmdc` 时输出 PNG；否则降级为代码块
- **数学公式** — 基础 LaTeX → OMML
- **题注与交叉引用** — `{#fig:id}`、`[@fig:id]`、表格题注
- **目录与页码** — Word 原生域、页眉页脚
- **分页符** — Markdown 中 `<!-- pagebreak -->`
- **Frontmatter** — YAML 元数据（title、author、date 等）
- **企微导入** — `--preset wecom`（pandoc 管线）

详见 [预设](references/presets.md)、[往返转换](references/roundtrip.md)、[插件](references/plugins.md)。

## 示例

[examples/](examples/README.md) 含 7 份示范报告：技术、商业、学术、API、会议、AI 报告、中文报告 — 各有 `example.md` 与编译好的 `example.docx`。插件示例：[examples/plugins/](examples/plugins/)。

## Git 工作流

**Markdown 进 Git，DOCX 当构建产物：**

```gitignore
dist/docx/
*.docx
```

```yaml
- uses: sunliang11/md-to-docx/action@v3
  with:
    input: docs/report.md
    preset: technical
- uses: actions/upload-artifact@v4
  with:
    name: docx
    path: dist/docx
```

详见 [action/README.md](action/README.md)。路线图：[references/roadmap.md](references/roadmap.md)。

## 安装

### 环境要求

- **Python 3.10+**
- **pandoc 3.x** — 仅 `--engine pandoc` / `--preset wecom` 需要
- **mmdc** — 仅当需要 Mermaid 渲染为图片时（[installation.md](references/installation.md)）

### 从源码（开发）

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e ".[dev]"      # 或 -e ".[mcp]" / -e ".[web]"
./bin/convert report.md
```

**暂未发布 PyPI。** 计划包名：`md2docx-compiler` · 命令行：`md-to-docx`。请从源码安装，或使用 `pip install "git+https://github.com/sunliang11/md-to-docx.git"`。

**Mermaid 说明：** 未安装 `mmdc` 时 native 引擎仍可生成 DOCX，图表显示为源码代码块；可用 `--strict-mermaid` 强制失败。完整说明见 [installation.md](references/installation.md)。

## 文档

- [安装与排错](references/installation.md)
- [预设模板](references/presets.md)
- [文档校验](references/validation.md)
- [往返 / reverse / diff](references/roundtrip.md)
- [Plugin API](references/plugins.md)
- [MCP 服务](references/mcp.md)
- [配合 AI 使用](references/agents.md)
- [GitHub Action](action/README.md)
- [Web Playground](web/README.md)
- [浏览器扩展](browser-extension/README.md)
- [VS Code 扩展](editors/vscode/README.md)
- [Obsidian 插件](editors/obsidian/README.md)
- [示例库](examples/README.md)
- [插件示例](examples/plugins/)
- [环境变量](references/configuration.md)
- [企微导入](references/wecom-import.md)
- [开发与测试](references/development.md)
- [发布流程](references/release.md)
- [路线图](references/roadmap.md)

## Cursor Skill

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

详见 [SKILL.md](SKILL.md)。

## License

MIT — 见 [LICENSE](LICENSE)。

---

## Star History

GitHub 在 2026 年限制了公开 stargazer API，因此大多数仓库无法使用 `api.star-history.com` 徽章。本图表由 [`.github/workflows/star-history.yml`](.github/workflows/star-history.yml) 生成并提交到仓库。

<!-- star-history:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/star-history/star-history-dark.svg">
  <img alt="Star history" src="assets/star-history/star-history-light.svg">
</picture>
<!-- star-history:end -->
