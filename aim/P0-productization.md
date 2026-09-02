# P0 — 项目产品化（v0.1.x）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** [`00-INDEX.md`](00-INDEX.md), [`aim.md`](aim.md)「Phase 0」
> **Depends on:** none
> **Unblocks:** P1A
> **Target version:** keep `0.1.0` until this plan's last task; then bump to `0.1.1` only if you ship behavior changes. Branding-only can stay `0.1.0`.
> **Estimated scope:** 1–2 days for an AI agent. No engine rewrite.

---

## Execution contract

### Goal

让陌生人打开 GitHub 仓库 10 秒内知道：这是 AI 时代的开源文档编译器，能把 Markdown / AI 生成内容变成可交付的专业 Word。然后一条命令就能跑通。

### 禁止（违反即失败）

- Web SaaS、MCP、浏览器插件、VS Code、Obsidian、Template Marketplace、新的 AI Agent 产品
- 重写转换引擎、引入 Document AST、换掉 pandoc
- 删除 WeCom / 企微导入能力
- 发布 PyPI（包名 `md-to-docx` 已被占用，P1D 再拍板）
- 把 README 第一屏继续写成「企微专用小工具」
- 大改 `scripts/md_to_docx/` 的转换逻辑（本阶段只允许为 examples / demo 需要的最小 CLI 文案改动）

### 允许改动的目录

- `README.md` / `README.zh.md`
- `SKILL.md`（只改定位句，不改工作流）
- `CHANGELOG.md` / `CONTRIBUTING.md`
- `examples/`（新建）
- `assets/branding/`、`assets/demo/`（新建）
- `.github/`（模板、Dependabot、Release、CODEOWNERS、SECURITY.md）
- `pyproject.toml`（description / keywords / urls 文案，不改依赖除非例子脚本需要）
- `references/`（增加 `examples.md` 链接，不重写转换原理）

### Done when

- [ ] GitHub 第一屏：定位句 + Before/After + 一条安装/运行命令 + Demo
- [ ] `examples/` 七套样例齐全，每套能被当前 CLI 转出非空 `.docx`
- [ ] Issue / PR 模板、SECURITY.md、Dependabot、Release workflow 存在
- [ ] 现有 `pytest tests/ -v` 全绿
- [ ] WeCom 文档入口仍在 README 里，但是「Preset / 使用场景」而不是唯一身份

---

## 当前状态（2026-09-02 已核对）

第一屏现状（`README.md` L3–L13）：标题 `md-to-docx`，副标题是 WeCom smart-document import，管道写死 pandoc。

已有工程化：`.github/workflows/ci.yml`、`.github/workflows/star-history.yml`、`CHANGELOG.md`、`CONTRIBUTING.md`、`LICENSE`（MIT）。

没有：`examples/`、Issue 模板、PR 模板、CODEOWNERS、Dependabot、SECURITY.md、Release workflow、Logo、Demo GIF。

CLI 可用：

```bash
./bin/convert report.md
python -m md_to_docx report.md
python -m md_to_docx ./docs --output-dir ./output --dry-run
```

转换不修改源 `.md`。默认排除 `README.md`、`CHANGELOG.md`、`SKILL.md`、`.github/**`。

---

## 锁定决策（不要再讨论）

1. **产品一句话（英文，README H1 下）：** `The open-source document compiler for the AI era.`
2. **产品一句话（中文）：** `把 Markdown / AI 生成内容，编译成可交付的专业 Word 文档。`
3. **视觉：** 极简 `MD → DOCX` 或 `# → W`。单色，适配 GitHub 亮/暗。不做复杂吉祥物。
4. **WeCom：** 保留，降为使用场景和 `--` 文档里的「企业微信导入」。本阶段不加 `--preset` flag（那是 P1B/P1D）。
5. **PyPI：** 本阶段不发布。README 继续诚实写「从源码安装」。
6. **Demo：** 两层。Layer A（必须）：CLI 终端 GIF + 静态 Markdown / 伪 Word 对比图。Layer B（人类可选）：用 Word / 企微真机截图替换伪 Word 图。
7. **Examples 的 `.docx`：** 提交到 git，让 GitHub 可预览下载。生成脚本必须可重复。`.gitignore` 里 `tests/fixtures/*.docx` 保持忽略，不要误伤 `examples/**/*.docx`。
8. **品牌文件前缀：** `assets/branding/logo.svg`、`assets/demo/hero.gif`。

---

## Task 0 — 建立本 plan 的工作分支约定

**不做 git 操作，除非用户要求。** 只在工作区改文件。

确认仓库可运行：

```bash
python3 -m pytest tests/ -v
./bin/convert --help
python -m md_to_docx --version
```

期望：测试通过；help 含 `--dry-run` `--output-dir`；version 含 `0.1.0`。

失败则先修环境（pandoc、`pip install -e ".[dev]"`），不要开始 Task 1。

---

## Task 1 — 重写 README 第一屏（英文）

**文件：** `README.md`（整页重构，保留后半的文档链接 / Skill / License / Star History）

### 第一屏必须按这个结构写（顺序锁定）

1. 语言切换：`English | [中文](README.zh.md)`
2. Badge 行：License、CI（`https://github.com/sunliang11/md-to-docx/actions/workflows/ci.yml`）、Python 3.10+。不要加假的 PyPI badge。
3. H1：`md-to-docx`
4. 定位句（英文）+ 一行解释：`Turn Markdown and AI-generated content into professional Word documents.`
5. 三个链接式 CTA（Markdown 链接，不是尚未存在的网站）：
   - `[Documentation](references/installation.md)`
   - `[Examples](examples/README.md)`
   - `[GitHub](https://github.com/sunliang11/md-to-docx)`
6. Hero 图：`assets/demo/hero.gif`（Task 4 会生成；先写 img 标签，Task 4 落地文件）
7. Before / After 小节：左 Markdown 代码块（短），右指向 `assets/demo/after.png` 或伪 Word 预览图
8. Quick Start：git clone + `./bin/convert report.md`（skill-first，不要把 pip 当第一路径）
9. Pipeline 一行：`Markdown / AI output → md-to-docx → Professional DOCX`
10. Features 短列表（只写**现在真的有的**）：
    - Headings, lists, tables, code blocks, blockquotes, images
    - CJK-aware reference template
    - Mermaid diagrams → PNG
    - Batch directory conversion
    - Cursor Agent Skill
    - WeCom smart-doc import (optional workflow)
11. 「What's next」用 3 行指向 AST / templates / AI 入口，明确这些是 roadmap，不要假装已经有 Web Playground
12. 原有 Documentation / Cursor Skill / License / Star History 区块保留并更新文案

### 关键词（自然写进第一段和 Features，不要堆砌 keyword stuffing）

`markdown to docx`、`markdown to word`、`AI to Word`、`ChatGPT to Word`、`document compiler`

### 不要写的句子

- 「Batch-convert Markdown to Word DOCX for WeCom」作为第一句
- 「Not published on PyPI」放第一屏（放到 Install 小节即可）
- 任何「Online Playground」死链

### 安装小节要求

保留两条路径：

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
./bin/convert path/to/report.md
```

和可选 `pip install -e .`。Requirements 写清：Python 3.10+、pandoc 3.x、mmdc 仅 Mermaid 需要。

### 完成定义

- 打开 `README.md`，前 40 行不出现「企业微信」/「WeCom」作为主定位（WeCom 可以在 Features 或后文出现）
- 前 40 行包含 `document compiler` 或 `AI-generated content`
- Star History HTML 注释块 `<!-- star-history:start -->` 原样保留

---

## Task 2 — 重写 README.zh.md 第一屏

**文件：** `README.zh.md`

与英文版结构一一对应。定位句用：

```
# md-to-docx

AI 时代的开源文档编译器。

把 Markdown / AI 生成内容，编译成可交付的专业 Word 文档。
```

WeCom 放在「使用场景」：

```markdown
## 使用场景

- 把 ChatGPT / Claude / Cursor 的 Markdown 变成可提交的 Word
- 技术方案、周报、API 文档、会议纪要
- 企业微信智能文档导入（保留原有优化管道）
```

完成定义：中英文 CTA / 章节顺序一致；中文第一屏不以企微为主定位。

---

## Task 3 — Logo / 品牌 SVG

**新建：**

```
assets/branding/logo.svg          # 正方形 icon，GitHub 头图可用
assets/branding/wordmark.svg      # 横版 MD → DOCX
assets/branding/README.md         # 使用说明（尺寸、颜色、在哪引用）
```

### 视觉规格（锁定）

- 画板：`logo.svg` 128×128；`wordmark.svg` 640×128
- 背景：透明
- 前景：`#111827`（near-black）。不要渐变、不要阴影、不要 3D
- logo 内容：上半 `#` 或 `MD`，中间细箭头 `↓`，下半 `W` 或 `DOCX`
- 深色模式：README 用 `<picture>` 不是必须。SVG 用 `currentColor` 或纯深色即可（GitHub 亮色 README 为主）
- 禁止：吉祥物、照片、AI 网红风紫渐变、超过 2 种颜色

`assets/branding/README.md` 写：

```markdown
# Branding

- `logo.svg` — icon
- `wordmark.svg` — MD → DOCX wordmark

Primary ink: #111827
Do not add colors, mascots, or gradients without a new branding task.
```

README 第一屏在 H1 旁或 H1 下嵌入：

```markdown
<img src="assets/branding/wordmark.svg" alt="md-to-docx: MD → DOCX" width="320">
```

### 完成定义

- 两个 SVG 可在浏览器打开，路径闭合，无外部字体依赖
- `README.md` 引用 wordmark 的相对路径正确

---

## Task 4 — Demo GIF + Before/After 静图

**新建：**

```
assets/demo/README.md
assets/demo/hero.gif          # CLI 演示，≤ 8MB，建议 < 3MB
assets/demo/before.md.png     # 源 Markdown 视觉
assets/demo/after.png         # 专业文档观感（允许 HTML 伪 Word）
scripts/demo/record_hero.sh   # 可重复生成
scripts/demo/render_after.py  # 可重复生成 after.png
```

### 4.1 Hero 叙事（10 秒内看懂）

画面顺序锁定：

1. 终端：`./bin/convert examples/technical-report/example.md`
2. 输出：`done: 1/1 succeeded`
3. 提示生成了 `example.docx`
4. （可选最后一帧）after.png 的专业文档画面

不要做「拖入文件 / 选择 Technical Report / Generate」这种 Web UI 叙事——Web 不存在。本阶段 Demo 必须诚实：这是 CLI。

### 4.2 生成方式（按可用性降级，不要卡住）

**优先 A — vhs（推荐）**

若本机有 [vhs](https://github.com/charmbracelet/vhs)：

```bash
which vhs || brew install vhs
```

新建 `scripts/demo/hero.tape`（vhs 脚本），录制真实命令。输出 `assets/demo/hero.gif`。

**优先 B — asciinema + agg**

```bash
asciinema rec /tmp/md-to-docx.cast
# 跑 ./bin/convert examples/technical-report/example.md
agg /tmp/md-to-docx.cast assets/demo/hero.gif
```

**允许 C — 静态帧合成 GIF（无录屏工具时）**

用 Python `pillow` 生成 4–6 帧伪终端画面（黑底绿/白字，等宽字体），合成 GIF。在 `assets/demo/README.md` 标明 `placeholder — replace with real recording`。

**禁止：** 下载网图当 Demo；用无关项目的 GIF。

### 4.3 After 图

写 `scripts/demo/render_after.py`：用 Pillow 画一张「Word 纸面」：

- 白底，浅灰页边
- 标题「Technical Report」
- H2「Architecture」
- 一段中英混排
- 一个三列表格
- 一个深色代码块

导出 `assets/demo/after.png`（宽 900px）。这是占位专业感，Task 完成后在 `assets/demo/README.md` 写：`Human: replace after.png with a real Word / WeCom screenshot when available.`

Before 图：把 `examples/technical-report/example.md` 前 30 行用 Pillow 画成等宽文本图 `before.md.png`。

### 4.4 README 引用

```markdown
![Convert Markdown to DOCX](assets/demo/hero.gif)

**Before** (Markdown) → **After** (Word)

<img src="assets/demo/before.md.png" width="48%"> <img src="assets/demo/after.png" width="48%">
```

### 完成定义

- `assets/demo/hero.gif` 存在且 > 10KB
- `before.md.png` / `after.png` 存在
- README 图片相对路径能解析
- `scripts/demo/` 里有可重复脚本；README.zh 同步引用

---

## Task 5 — Examples 库

**新建目录（名称锁定，与 aim.md 一致）：**

```
examples/
├── README.md
├── technical-report/
├── business-report/
├── academic-paper/
├── api-document/
├── meeting-notes/
├── ai-report/
└── chinese-report/
```

每个子目录必须有：

```
example.md
example.docx
preview.png
README.md
```

### 5.1 每个 example.md 的内容规格

| 目录 | 主题 | 必须包含的 Markdown 结构 |
|------|------|--------------------------|
| technical-report | 系统设计（可虚构「文档编译器架构」） | H1–H3、表格、代码块、Mermaid flowchart、中英混排 |
| business-report | 季度业务综述 | H1–H2、KPI 表格、引用块、无序列表 |
| academic-paper | 短论文结构 | Abstract、编号列表、引用块、一张表 |
| api-document | HTTP API | 标题、代码块（json/http）、参数表 |
| meeting-notes | 会议纪要 | 任务列表 `- [ ]`、日期、决策列表 |
| ai-report | 模拟 Claude/ChatGPT 导出的技术方案 | 典型 AI 腔但结构完整：Overview / Design / Risks |
| chinese-report | 纯中文技术方案 | 中文标题「一、二、三」、中文表格、中文代码注释 |

每个 `example.md`：80–200 行。不要空壳标题。technical-report 必须含一个 ```` ```mermaid ```` flowchart（CI 里 examples 转换可以 skip mermaid 若无 mmdc——见 5.4）。

YAML frontmatter 可以写但不被当前引擎消费。允许：

```markdown
---
title: Technical Report
author: md-to-docx
---
```

### 5.2 每个子 README.md

固定小节：

```markdown
# <Name>

What this example shows.

## Convert

```bash
./bin/convert examples/<dir>/example.md
```

Output: `examples/<dir>/example.docx`
```

### 5.3 examples/README.md

表格列出 7 个例子 + 一句话 + 链接。顶部说明：

```markdown
These examples are converted with the current pandoc pipeline (v0.1).
Native Document AST lands in v0.2 (see aim/P1A-document-engine.md).
```

### 5.4 生成 docx 与 preview

新建 `scripts/demo/build_examples.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/scripts${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"
for d in examples/*/ ; do
  python3 -m md_to_docx "${d}example.md"
done
```

对 technical-report：若无 `mmdc`，example.md 仍可保留 mermaid 块，但 `build_examples.sh` 在无 mmdc 时打印 skip 并失败码 0 之外的提示——**更好的做法：** technical-report 的 mermaid 保留，文档写清需要 mmdc；CI 的 examples job 安装 mermaid-cli 太重，P0 的 CI **不要** 强依赖 mermaid。因此：

- `technical-report/example.md` 的 mermaid 用一个**小** flowchart（< 15 行）
- `build_examples.sh`：检测到 mermaid 且无 mmdc 时，对该文件用 `sed` 临时注释？**不要改源文件。**
- 锁定：本机生成 `example.docx` 时，执行者必须有 pandoc。Mermaid 文件：如果转换因缺 mmdc 失败，把该 mermaid 块改成「已渲染示意图」的普通 `![architecture](preview-architecture.png)` **另外**保留一份 `diagram.mmd.md`？太碎。

**最终锁定：** 7 个例子里只有 `technical-report` 含 mermaid。`build_examples.sh` 若 `mmdc` 缺失，对 technical-report 打印 warning 并继续（转换会失败）——不行。

改为：P0 的 `technical-report/example.md` **内嵌 mermaid，同时提交一张** `architecture.png`（可用 Task 4 的 Pillow 画框图）。正文用：

````markdown
```mermaid
flowchart LR
  A[Markdown] --> B[md-to-docx] --> C[DOCX]
```
````

以及：

```markdown
![Architecture](architecture.png)
```

这样无 mmdc 时，CLI 仍因 mermaid 失败。所以 **P0 technical-report 不要放 mermaid fence**。在该例 README 写：`Mermaid fences are supported by the converter when mmdc is installed. This example uses a static PNG so the example builds anywhere with pandoc.`

差异化 mermaid 演示放到 P1C。P0 只承诺：例子能在「仅 pandoc」环境转成功。

### 5.5 preview.png

每个例子用 Pillow 生成一张 800px 宽的「第一页预览」占位图（标题 + 2 段文字），文件名 `preview.png`。`scripts/demo/render_previews.py` 读取 example.md 的 H1 和前 2 个段落生成。人类以后可替换成真 Word 截图。

### 5.6 .gitignore

确认 `tests/fixtures/*.docx` 不会忽略 `examples/**/example.docx`。当前规则是 `tests/fixtures/*.docx`，安全。不要加 `*.docx` 全局忽略。

### 完成定义

```bash
bash scripts/demo/build_examples.sh
test -s examples/technical-report/example.docx
test -s examples/chinese-report/example.docx
# 7 个 docx 都非空
find examples -name example.docx | wc -l   # = 7
```

`./bin/convert examples/meeting-notes/example.md` 退出码 0。

---

## Task 6 — GitHub 工程化

### 6.1 Issue templates

新建：

```
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
```

`config.yml`：

```yaml
blank_issues_enabled: false
contact_links:
  - name: Documentation
    url: https://github.com/sunliang11/md-to-docx/blob/main/references/installation.md
    about: Install, pandoc, mermaid troubleshooting
```

`bug_report.yml` 必填字段：

- 描述
- 复现步骤
- 期望 / 实际
- `md-to-docx --version` 输出
- `pandoc --version` 第一行
- OS
- 是否含 Mermaid
- 可附最小 `.md` 片段（textarea）

`feature_request.yml` 必填：问题、建议、是否愿提交 PR。描述里加一句：Phase 0 不接受 Web/MCP/插件类功能请求作为「现在就做」（可记 roadmap）。

### 6.2 PR 模板

新建 `.github/pull_request_template.md`：

```markdown
## Summary

## Test plan

- [ ] `pytest tests/ -v`
- [ ] `./bin/convert --help`

## Docs

- [ ] CHANGELOG.md updated if user-visible
```

### 6.3 CODEOWNERS

新建 `.github/CODEOWNERS`：

```
* @sunliang11
```

若 GitHub 用户名不是 sunliang11，改为仓库 owner。从 `git remote get-url origin` 读取。

### 6.4 Dependabot

新建 `.github/dependabot.yml`：

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

### 6.5 SECURITY.md

新建仓库根 `SECURITY.md`：

- 支持版本：当前 `0.1.x`
- 报告方式：GitHub Security Advisory（private）
- 不要承诺 SLA

### 6.6 Release workflow

新建 `.github/workflows/release.yml`：

- trigger：`push tags: ['v*']`
- jobs：checkout、setup-python 3.12、`pip install -e ".[dev]" build`、`pytest`、`python -m build`
- 用 `softprops/action-gh-release@v2` 把 `dist/*.whl` `dist/*.tar.gz` 挂到 GitHub Release
- **不要** 配置 PyPI publish
- 需要 `permissions: contents: write`

### 6.7 CI 小增强（不要大改）

编辑 `.github/workflows/ci.yml`，在现有 test job 之后或同一 job 末尾加：

```yaml
      - name: Convert examples (pandoc only)
        run: |
          for f in examples/*/example.md; do
            python -m md_to_docx "$f"
            test -s "${f%.md}.docx"
          done
```

若 examples 尚未在同一 PR 落地，这个 step 必须和 Task 5 同一批提交，否则 CI 红。

给 `contributors` 权限无变化。不要加 mermaid-cli 安装（太慢/易碎）。

### 完成定义

- 上述文件都存在且 YAML 可被 GitHub 解析（缩进 2 空格）
- CI 文件仍在 3.10/3.11/3.12 matrix 跑 pytest
- 无 PyPI token / secret 引用

---

## Task 7 — 文案对齐（包元数据、Skill、贡献指南）

### 7.1 pyproject.toml

更新：

```toml
description = "The open-source document compiler for the AI era. Markdown / AI output → professional DOCX."
keywords = ["markdown", "docx", "word", "pandoc", "ai", "document-compiler", "mermaid", "wecom"]
```

增加：

```toml
[project.urls]
Homepage = "https://github.com/sunliang11/md-to-docx"
Documentation = "https://github.com/sunliang11/md-to-docx#readme"
Issues = "https://github.com/sunliang11/md-to-docx/issues"
```

不要改 `name = "md-to-docx"`（本地包名可保持；反正不发 PyPI）。不要改 version。

### 7.2 SKILL.md

只改 `description` 和 H1 下第一句，让 Agent 知道产品定位变了，但 **工作流步骤保持 skill-first / 禁止乱 pip**。

description 建议：

```
Converts Markdown and AI-generated content to professional Word DOCX (pandoc + optional mermaid-cli).
WeCom smart-doc import remains a supported workflow. Use when the user wants md→docx, batch convert, or 企微导入.
```

Agent workflow 6 步不要删。

### 7.3 CONTRIBUTING.md

在 Project layout 加上 `examples/`、`assets/branding/`、`assets/demo/`。

加一节 **Scope**：

```markdown
## Scope (Phase 0)

Please do not open PRs for a web app, MCP server, browser extension, or marketplace.
The current milestone is: make Markdown → DOCX excellent and the GitHub page trustworthy.
See `aim/` for the roadmap.
```

### 7.4 CHANGELOG.md

在 `[Unreleased]` Added：

- Reposition README as an AI-era document compiler (WeCom remains a supported workflow)
- Examples gallery
- GitHub issue/PR templates, SECURITY.md, Dependabot, release workflow
- Branding and demo assets

### 7.5 references/installation.md

开头加 3 行指向新定位，安装步骤不改。

新建 `references/roadmap.md`：10 行，链到 `aim/00-INDEX.md`，避免用户以为 Web 已经存在。

README Documentation 列表加上 Roadmap 链接。

### 完成定义

```bash
python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['description'])"
```

输出含 `document compiler`。`SKILL.md` frontmatter 仍只有 `name` 和 `description` 两键（现有约定）。

---

## Task 8 — 回归与验收

按顺序跑：

```bash
pip install -e ".[dev]"
pytest tests/ -v
./bin/convert --help
python -m md_to_docx --version
python -m md_to_docx tests/fixtures/sample.md --output-dir /tmp/md2docx-p0
test -s /tmp/md2docx-p0/sample.docx
bash scripts/demo/build_examples.sh
find examples -name example.docx -size +1k | wc -l
```

期望：

- pytest 全绿（与 P0 之前数量相比不允许减少）
- examples 7 个 docx 都 > 1KB
- README.md 相对图片全部存在：

```bash
python3 - <<'PY'
from pathlib import Path
import re
text = Path("README.md").read_text()
paths = re.findall(r"\((assets/[^)]+)\)", text)
paths += re.findall(r'src="(assets/[^"]+)"', text)
missing = [p.split()[0] for p in paths if not Path(p.split()[0]).exists()]
print("checked", len(paths), "missing", missing)
raise SystemExit(1 if missing else 0)
PY
```

### README 人工检查清单（agent 用 Read 工具自检）

- [ ] 第一屏不是 WeCom-first
- [ ] 有 wordmark 或 logo
- [ ] 有 hero.gif
- [ ] 有 examples 链接
- [ ] clone + `./bin/convert` 仍是最快路径
- [ ] Star History 块未损坏
- [ ] 中文 README 同步

---

## Out of scope（记入 P1+，本 plan 禁止做）

- Document AST / 换引擎
- `--template` `--preset`
- 原生 TOC / 页眉 / OMML
- PyPI 改名发布
- 网站
- 把 WeCom Lua filter 删掉

---

## Handoff to P1A

P0 完成后，产品看起来像成熟开源项目，引擎仍是 pandoc。

P1A 将引入 `Document AST`，并把 pandoc 变成 `--engine pandoc` fallback。不要在 P0 预埋空的 `ast/` 包。

---

## Execution log

**2026-09-02** — P1A–P1D implemented. v1.0.0. pytest 92 passed. Native engine default.
