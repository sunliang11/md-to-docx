# md-to-docx 分阶段实现计划（执行总表）

> 产品战略原文：[`aim.md`](aim.md)
> 仓库快照日期：2026-09-02
> 当前版本：`0.1.0`（Beta，未上 PyPI）
> 当前定位：WeCom 企微导入专用 Markdown → DOCX（pandoc 管道）
> 目标定位：AI / Markdown → Professional Document 的开源文档编译基础设施

---

## 给执行本计划的 AI Agent

你一次只执行 **一个** plan 文件。不要跨阶段提前实现 Web / MCP / 浏览器插件 / VS Code / Marketplace。

### 开工前必读（按顺序）

1. 本文件（知道现在该做哪一份）
2. [`aim.md`](aim.md) 对应阶段的「目标 / 不要做什么」
3. 当前要执行的那份 `P*.md`
4. 仓库真实代码：`scripts/md_to_docx/`、`tests/`、`README.md`、`pyproject.toml`

### 执行协议

1. 打开本文件，找到第一个 **Status = `TODO`** 且依赖已全部 `DONE` 的 plan。
2. 把该 plan 的 Status 改成 `IN PROGRESS`。
3. 严格按该 plan 的 Task 顺序做。每个 Task 都有：改哪些文件、怎么实现、怎么验证、完成定义。
4. 不要做该 plan「Out of scope」和「禁止」列出的事。
5. 全部 Task 的验收命令通过后，把 Status 改成 `DONE`，并更新本文件的勾选框。
6. 停下来。把验证证据（命令 + 关键输出）写进该 plan 文末 `## Execution log`。等人类确认后再开下一份。
7. 不要在本阶段提交「顺手重构」。现有 pandoc 管道在 P1A 完成前必须继续可用。

### 硬约束（所有阶段通用）

- 不要把核心引擎闭源，不要做成必须绑定某一家 AI API 的 wrapper。
- 不要让 DOCX API 泄漏进 Markdown Parser。
- 不要为单个场景堆 `if template == "..."`。
- 不要删除 WeCom 能力：它变成 `--preset wecom`，不是被扔掉。
- 不要在 Phase 0 做引擎重写。
- 测试：每个行为变化必须有 pytest；DOCX 质量用 XML 断言（参考 `tests/test_docx_output.py`）。
- 用户可见变化写入 `CHANGELOG.md`。
- 未经用户明确要求，不要 `git commit` / `git push`。

### 完成一个 plan 的最低证据

```bash
pip install -e ".[dev]"
pytest tests/ -v
python -m md_to_docx --help
./bin/convert --help
```

个别 plan 会追加自己的验收命令。那些命令也必须通过。

---

## 当前仓库事实（写计划时已核对）

| 已有 | 没有 |
|------|------|
| CLI：`python -m md_to_docx` / `bin/convert` | Document AST |
| pandoc + Lua filter + `reference-wecom.docx` | 原生 DOCX Renderer |
| Markdown normalizer | `--template` / `--preset`（除 WeCom 写死） |
| Mermaid → PNG（mmdc） | 原生 TOC / 页眉页脚 / OMML 公式 |
| pytest + CI（3.10/3.11/3.12） | `examples/` 展示库 |
| CHANGELOG / CONTRIBUTING / MIT LICENSE | Logo、Demo GIF、Before/After |
| 双语 README（但第一屏是企微工具） | Issue/PR 模板、CODEOWNERS、Dependabot、SECURITY.md、Release workflow |
| Cursor `SKILL.md` | MCP / Web / 浏览器插件 / VS Code / Action |

转换管道（现状）：

```
.md → normalize → mermaid PNG → pandoc + reference-wecom.docx + wecom-layout.lua → .docx
```

包布局：`scripts/md_to_docx/`（hatchling `dev-mode-dirs = ["scripts"]`）。P0/P1 不要把包搬到 `src/`。

PyPI 包名 `md-to-docx` **已被占用**。GitHub 仓库名保持 `md-to-docx`。发布名在 P1D 才拍板，P0 不发 PyPI。

---

## 阶段地图

```
P0 产品化          ── 让 GitHub 第一屏像成熟开源项目
        │
        ▼
P1A Document Engine ── Parser → AST → Renderer（pandoc 降为 fallback）
        │
        ▼
P1B Template/TOC/CJK ── 模板系统、目录、页眉页脚、中文质量
        │
        ▼
P1C Differentiator  ── Mermaid SVG、OMML 公式、Caption、交叉引用
        │
        ▼
P1D v1.0            ── Preset、质量闸门、发版
        │
        ▼
P2A Agent/MCP       ── Skill 矩阵 + MCP（AI 不进核心引擎）
        │
        ▼
P2B Web Playground  ── 30 秒体验 + Docker
        │
        ▼
P2C Browser Ext     ── Export AI to Word
        │
        ▼
P3A Roundtrip       ── DOCX↔MD、Diff、GitHub Action
        │
        ▼
P3B Editors/Plugins ── VS Code、Obsidian、最小 Plugin API
        │
        ▼
P4  Ecosystem       ── 模板市场、文档标准、Cloud（引擎继续开源）
```

版本对照（来自 `aim.md` §十二）：

| 版本 | Plan | 一句话 |
|------|------|--------|
| v0.1 | P0 | README / Branding / CI / Examples / Demo |
| v0.2 | P1A | Document AST + Parser + DOCX Renderer |
| v0.3 | P1B | Template + TOC + Header/Footer + CJK |
| v0.4 | P1C | Mermaid + Math + Caption + Cross-ref |
| v1.0 | P1D | Professional Markdown → DOCX |
| v1.5 | P2B | Web Playground + Docker + Presets 收口 |
| v2.0 | P2A | Agent Skill + MCP + AI → Word |
| v2.5 | P2C | Browser Extension |
| v3.0 | P3A | Roundtrip + Diff + Action + VS Code 起步 |
| v3.5 | P3B | Plugin API + Obsidian |
| v4.0 | P4 | Standard + Marketplace + Cloud |

---

## Plan 清单与状态

执行顺序就是表格顺序。把 `TODO` 改成 `IN PROGRESS` / `DONE`。

| # | 文件 | 阶段 | 目标版本 | 依赖 | Status |
|---|------|------|----------|------|--------|
| 0 | [00-INDEX.md](00-INDEX.md) | — | — | — | 本表 |
| 1 | [P0-productization.md](P0-productization.md) | Phase 0 | 0.1.x | 无 | TODO |
| 2 | [P1A-document-engine.md](P1A-document-engine.md) | Phase 1 | 0.2.0 | P0 | TODO |
| 3 | [P1B-template-toc-cjk.md](P1B-template-toc-cjk.md) | Phase 1 | 0.3.0 | P1A | TODO |
| 4 | [P1C-mermaid-math-caption.md](P1C-mermaid-math-caption.md) | Phase 1 | 0.4.0 | P1B | TODO |
| 5 | [P1D-v1-release.md](P1D-v1-release.md) | Phase 1 | 1.0.0 | P1C | TODO |
| 6 | [P2A-agent-mcp.md](P2A-agent-mcp.md) | Phase 2 | 2.0.0 | P1D | DONE |
| 7 | [P2B-web-playground.md](P2B-web-playground.md) | Phase 2 | 1.5 / 2.0 | P1D | DONE |
| 8 | [P2C-browser-extension.md](P2C-browser-extension.md) | Phase 2 | 2.5.0 | P2A, P2B | DONE |
| 9 | [P3A-roundtrip-action.md](P3A-roundtrip-action.md) | Phase 3 | 3.0.0 | P2A | TODO |
| 10 | [P3B-editors-plugin-api.md](P3B-editors-plugin-api.md) | Phase 3 | 3.5.0 | P3A | TODO |
| 11 | [P4-ecosystem.md](P4-ecosystem.md) | Phase 4 | 4.0.0 | P3B | DONE |

P2A 与 P2B 可在 P1D 完成后并行（两个 agent / 两个分支），但不要和 P0–P1 并行。

---

## 北极星与阶段健康指标（不要把 Star 当硬 KPI）

北极星：**Monthly Documents Generated**（最终量级参考：100,000 / month）。

| 阶段 | Star 参考 | Release | 真正要盯的 |
|------|-----------|---------|------------|
| P0 | 0 → 50 | v0.1.x | 首页 10 秒看懂；clone 后 1 条命令出 DOCX |
| P1 | 50 → 500 | v1.0 | 转换质量（CJK、表格、代码块、目录） |
| P2 | 500 → 2K | v2.0 | AI 用户 30 秒出 Word（Playground / Skill / MCP） |
| P3 | 2K → 5K | v3.0 | 可编程文档（roundtrip、Action、插件） |
| P4 | 5K → 10K+ | v4.0 | 别人提交模板 / 插件 |

---

## 架构终局（后面所有 plan 必须朝这里收敛）

```
Input: Markdown | DOCX | AI Markdown
        ↓
     Parser
        ↓
   Document AST
        ↓
 Transformer / Template / Plugin
        ↓
     Renderer
        ↓
   DOCX (第一公民) | PDF | HTML
```

外围入口（按阶段解锁，禁止提前）：CLI → Skill → MCP → Web → Browser → Action → VS Code → Obsidian。

DOCX 永远是第一公民。不要做成万能格式转换器。
