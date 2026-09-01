[English](README.md) | 中文

# md-to-docx

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

批量转换 Markdown 为 Word DOCX，用于**企业微信智能文档导入**。

## 功能说明

将 Markdown 文件转换为针对企微「导入本地文档」优化的 Word 文档。代码块、表格、标题和中文文本的保留效果优于直接粘贴 Markdown。

**处理流程：** `.md` → 规范化空白 → 可选 Mermaid→PNG → pandoc 配合自定义参考模板 + Lua 过滤器 → `.docx`

## 状态

**Beta (0.1.0)。** 未发布到 PyPI —— PyPI 上的 `md-to-docx` 包名属于另一个项目。请从源代码安装。

## 快速开始

### 环境要求

- **Python 3.10+**
- **pandoc 3.x** —— Markdown → DOCX 转换
- **mmdc** (可选) —— 仅当 `.md` 包含 ` ```mermaid ` 代码块时需要

### 安装

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .
```

### 运行

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
- [环境变量](references/configuration.md)
- [企微导入指南](references/wecom-import.md)
- [开发与测试](references/development.md)

## Cursor Skill

将本仓库软链接到 `~/.cursor/skills/md-to-docx` 即可用作 Cursor Agent 技能：

```bash
ln -sfn /path/to/md-to-docx ~/.cursor/skills/md-to-docx
```

Agent 使用说明见 [SKILL.md](SKILL.md)。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。

---

## Star History

GitHub 于 2026 年限制了公共 stargazer API 访问权限，因此托管的 `api.star-history.com` 徽章对大多数仓库不再有效。此图表由 [`.github/workflows/star-history.yml`](.github/workflows/star-history.yml) 生成并提交到仓库。

<!-- star-history:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/star-history/star-history-dark.svg">
  <img alt="Star history" src="assets/star-history/star-history-light.svg">
</picture>
<!-- star-history:end -->
