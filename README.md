# md-to-docx

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Batch-convert Markdown to DOCX for **WeCom (企业微信) smart-document import** —「导入本地文档」.

Also a [Cursor Agent Skill](SKILL.md): symlink this repo to `~/.cursor/skills/md-to-docx`.

---

## English

### What it does

Converts Markdown files to Word documents optimized for WeCom import. Tables, nested lists, heading hierarchy, and embedded images survive better than pasting raw Markdown.

Pipeline:

```
.md → normalize → mermaid→PNG → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

### Quick start

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .
python3 -m md_to_docx ./docs          # directory (recursive)
python3 -m md_to_docx report.md      # single file
```

> **Note:** Not published on PyPI. The PyPI package name `md-to-docx` belongs to a different project.

### Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | **3.10+** | Run the converter |
| **pandoc** | 3.x | Markdown → DOCX |
| **mmdc** | Latest | Only when `.md` contains ` ```mermaid ` blocks |
| **python-docx** | 1.0+ | Only when rebuilding the Word reference template |

### Install as Cursor Skill

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

The folder name must match the skill `name` (`md-to-docx`). Agent instructions: [SKILL.md](SKILL.md).

### Documentation

| Topic | File |
|-------|------|
| Installation & troubleshooting | [references/installation.md](references/installation.md) |
| Environment variables | [references/configuration.md](references/configuration.md) |
| WeCom import & checklist | [references/wecom-import.md](references/wecom-import.md) |
| Development & tests | [references/development.md](references/development.md) |

### License

MIT — see [LICENSE](LICENSE).

---

## 中文

### 简介

将 Markdown 批量转换为 DOCX，用于**企业微信智能文档**的「导入本地文档」。相比直接粘贴 Markdown，表格、嵌套列表、标题层级和嵌入图片的保留效果更好。

处理流程：

```
.md → 规范化 → mermaid→PNG → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

### 快速开始

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .
python3 -m md_to_docx ./docs
```

> **说明：** 本项目未发布到 PyPI。PyPI 上的 `md-to-docx` 是另一个项目，请勿使用 `pip install md-to-docx`。

### 环境要求

| 组件 | 版本 | 用途 |
|------|------|------|
| **Python** | **3.10+** | 运行转换器 |
| **pandoc** | 3.x | Markdown → DOCX |
| **mmdc** | 最新版 | 仅当含 mermaid 代码块时 |
| **python-docx** | 1.0+ | 仅重建 Word 参考模板时 |

### 安装为 Cursor Skill

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

目录名须与 skill `name` 一致（`md-to-docx`）。Agent 使用说明见 [SKILL.md](SKILL.md)。

### 文档

| 主题 | 文件 |
|------|------|
| 安装与排错 | [references/installation.md](references/installation.md) |
| 环境变量 | [references/configuration.md](references/configuration.md) |
| 企微导入与验收 | [references/wecom-import.md](references/wecom-import.md) |
| 开发与测试 | [references/development.md](references/development.md) |

### 许可证

MIT — 见 [LICENSE](LICENSE)。

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sunliang11/md-to-docx&type=Date)](https://star-history.com/#sunliang11/md-to-docx&Date)
