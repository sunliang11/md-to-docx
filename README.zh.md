[English](README.md) | 中文

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml/badge.svg)](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

# md-to-docx

<img src="assets/branding/wordmark.svg" alt="md-to-docx: MD → DOCX" width="320">

**AI 时代的开源文档编译器。**

把 Markdown 与 AI 生成内容编译成可交付的专业 Word 文档。

[文档](references/installation.md) · [示例](examples/README.md) · [GitHub](https://github.com/sunliang11/md-to-docx)

![Markdown 转 DOCX 演示](assets/demo/hero.gif)

**转换前**（Markdown）→ **转换后**（Word）

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">

## 快速开始

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md --preset technical
```

无需安装 Python，可用 Docker 试用 Playground：

```bash
docker compose -f web/docker-compose.yml up --build
# 浏览器打开 http://localhost:8080
```

**处理流程：** Markdown / AI 输出 → Document AST → 专业 DOCX

**状态：1.0 引擎 + v2 AI 入口** — 默认 native Document AST；MCP、Web Playground、浏览器扩展，本地 AI → Word，无需 API Key。企微导入：`--preset wecom`。

## 功能特性

- 原生 Document AST 引擎（默认）— 多数场景无需 pandoc
- 标题、列表、表格、代码块、引用块、图片、脚注
- CJK 中文模板（微软雅黑 / 宋体）
- Mermaid 图表 → PNG（需 mmdc；未安装时 native 引擎降级为代码块）
- 数学公式 → OMML（基础 LaTeX）
- 图/表题注与交叉引用
- 模板预设：`--preset technical|academic|business|professional|report`
- Word 原生目录（`--toc`）、页码、页眉页脚
- `--check` 文档校验（不生成 docx）
- 批量目录转换
- Cursor Agent Skill
- 企业微信智能文档导入（`--preset wecom` 或 `--engine pandoc`）
- MCP 服务（`md-to-docx-mcp`）— 见 [配合 AI 使用](#配合-ai-使用)
- Web Playground（Docker）— 浏览器编辑并下载 DOCX
- 浏览器扩展 — 从 AI 对话导出 Word

## 配合 AI 使用

把 AI 写的 Markdown 转成 Word — **无需 API Key**，全部本地：

| 入口 | 文档 |
|------|------|
| Cursor Skill | [SKILL.md](SKILL.md) |
| Claude Code / Codex | [skills/](skills/) |
| MCP | [references/mcp.md](references/mcp.md) — `pip install .[mcp]` |
| Web Playground | [web/README.md](web/README.md) — Docker |
| 浏览器扩展 | [browser-extension/README.md](browser-extension/README.md) |
| ChatGPT 提示词 | [references/agents.md](references/agents.md) |

## 后续规划

- **v3.0** — DOCX 往返 + GitHub Action（[路线图](references/roadmap.md)）

## 安装

### 环境要求

- **Python 3.10+**
- **pandoc 3.x** — 仅 `--engine pandoc` / `--preset wecom` 需要

### Mermaid 图表（mmdc）

仅当 Markdown 含 ` ```mermaid ` 代码块，且希望输出为**图片**时需要。不含 Mermaid 的文档无需安装。

**安装**（需要 Node.js / npm）：

```bash
npm install -g @mermaid-js/mermaid-cli

# 验证
mmdc --version
```

- **macOS：** 若未安装 npm，可先执行 `brew install node`
- **Linux：** 从发行版安装 Node.js 后执行上述命令

**浏览器：** `mmdc` 通过 Puppeteer 调用 Chromium 系浏览器（Chrome、Edge 或 Chromium）。也可设置 `MD_TO_DOCX_BROWSER` 或 `PUPPETEER_EXECUTABLE_PATH` — 详见 [环境变量](references/configuration.md)。

**未安装 mmdc 时：**

| 条件 | 结果 |
|------|------|
| 文档无 Mermaid | 不受影响 |
| Native 引擎（默认）+ 有 Mermaid | 可正常生成 DOCX；Mermaid 显示为**源码代码块**，stderr 有 warning |
| Native + `--strict-mermaid` | 缺 mmdc → 转换失败 |
| `--engine pandoc` / `--preset wecom` + 有 Mermaid | 转换失败，需安装 mmdc |
| Docker Playground（slim 镜像） | 同 Native 降级行为（代码块） |

渲染产物：native 引擎将 PNG/SVG 保存到 `{stem}-media/`；pandoc 引擎将 PNG 保存到 `{stem}mermaid图片/`。

详见 [安装与排错](references/installation.md)。

### 从源码运行（推荐）

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert report.md
./bin/convert ./docs          # 目录（递归）
```

### 可编辑安装（可选）

```bash
pip install -e .
pip install -e ".[mcp]"   # MCP 服务
pip install -e ".[web]"   # Playground API
```

PyPI 包名：`md2docx-compiler`（命令行仍为 `md-to-docx`）。

## 运行

```bash
# 转换单个文件
python -m md_to_docx report.md

# 转换目录（递归）
python -m md_to_docx ./docs

# 带选项
python -m md_to_docx ./docs --exclude "README.md" --output-dir ./output
```

CLI 选项：

- `--version` — 显示版本
- `--exclude PATTERN` — 排除匹配模式的文件（可多次使用）
- `--output-dir DIR` — 将 .docx 写入指定目录
- `--skip-existing` — 跳过已存在的输出
- `--dry-run` — 预览将要转换的文件

默认排除 `README.md`、`CHANGELOG.md`、`SKILL.md` 和 `.github/**`。自动跳过 `.git` 和 `node_modules`。

## 文档

- [安装与排错](references/installation.md)
- [预设模板](references/presets.md)
- [文档校验](references/validation.md)
- [MCP 服务](references/mcp.md)
- [配合 AI 使用](references/agents.md)
- [Web Playground](web/README.md)
- [浏览器扩展](browser-extension/README.md)
- [示例库](examples/README.md)
- [路线图](references/roadmap.md)
- [环境变量](references/configuration.md)
- [企微导入指南](references/wecom-import.md)
- [开发与测试](references/development.md)

**入口说明：** 人类访客：`README.md` / `README.zh.md`；Cursor：[SKILL.md](SKILL.md)；MCP：[references/mcp.md](references/mcp.md)；Playground：[web/README.md](web/README.md)；扩展：[browser-extension/README.md](browser-extension/README.md)。

## Cursor Skill

将本仓库软链接到 `~/.cursor/skills/md-to-docx`：

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

详见 [SKILL.md](SKILL.md) 中的 Agent 使用说明。

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
