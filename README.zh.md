[English](README.md) | 中文

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml/badge.svg)](https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

# md-to-docx

<img src="assets/branding/wordmark.svg" alt="md-to-docx: MD → DOCX" width="320">

**AI 时代的开源文档编译器。**

把 Markdown / AI 生成内容，编译成可交付的专业 Word 文档。

[文档](references/installation.md) · [示例](examples/README.md) · [GitHub](https://github.com/sunliang11/md-to-docx)

![Markdown 转 DOCX 演示](assets/demo/hero.gif)

**转换前**（Markdown）→ **转换后**（Word）

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">

## 快速开始

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md
```

**处理流程：** Markdown / AI 输出 → md-to-docx → 专业 DOCX

## 功能特性

- 标题、列表、表格、代码块、引用块、图片
- CJK 中文排版参考模板
- Mermaid 图表 → PNG
- 批量目录转换
- Cursor Agent Skill
- 企业微信智能文档导入（可选工作流）

## 使用场景

- 把 ChatGPT / Claude / Cursor 的 Markdown 变成可提交的 Word
- 技术方案、周报、API 文档、会议纪要
- 企业微信智能文档导入（保留原有优化管道）

## 后续规划

- **v0.2** — 原生 Document AST（[路线图](references/roadmap.md)）
- **v0.3** — 模板预设（学术、商务、API）
- **v0.4+** — AI 原生入口（规划中，尚未提供）

## 安装

### 环境要求

- **Python 3.10+**
- **pandoc 3.x** —— Markdown → DOCX 转换
- **mmdc**（可选）—— 仅当 `.md` 包含 ` ```mermaid ` 代码块时需要

### 从源码安装（推荐）

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert report.md
./bin/convert ./docs          # 目录（递归扫描）
```

### 可编辑安装（可选）

```bash
pip install -e .
```

未发布到 PyPI —— PyPI 上的 `md-to-docx` 包名属于另一个项目。

## 运行

```bash
# 转换单个文件
python -m md_to_docx report.md

# 转换目录（递归扫描）
python -m md_to_docx ./docs

# 使用选项
python -m md_to_docx ./docs --exclude "README.md" --output-dir ./output
```

CLI 选项：

- `--version` —— 显示版本
- `--exclude PATTERN` —— 排除匹配模式的文件（可多次使用）
- `--output-dir DIR` —— 将 .docx 文件写入指定目录
- `--skip-existing` —— 跳过已存在的输出文件
- `--dry-run` —— 预览将要转换的文件

默认排除 `README.md`、`CHANGELOG.md`、`SKILL.md` 和 `.github/**`。自动跳过 `.git` 和 `node_modules`。

## 文档

- [安装与排错](references/installation.md)
- [示例库](examples/README.md)
- [路线图](references/roadmap.md)
- [环境变量](references/configuration.md)
- [企微导入指南](references/wecom-import.md)
- [开发与测试](references/development.md)

**入口说明：** 人类访客看 `README.md` / `README.zh.md`；Cursor Agent 看 [SKILL.md](SKILL.md)；详细文档在 `references/`。

## Cursor Skill

将本仓库软链接到 `~/.cursor/skills/md-to-docx` 即可用作 Cursor Agent 技能：

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

详见 [SKILL.md](SKILL.md) 中的 Agent 使用说明。

## License

MIT —— 见 [LICENSE](LICENSE)。

---

## Star History

GitHub 在 2026 年限制了公开 stargazer API，因此大多数仓库无法使用 `api.star-history.com` 徽章。本图表由 [`.github/workflows/star-history.yml`](.github/workflows/star-history.yml) 生成并提交到仓库。

<!-- star-history:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/star-history/star-history-dark.svg">
  <img alt="Star history" src="assets/star-history/star-history-light.svg">
</picture>
<!-- star-history:end -->
