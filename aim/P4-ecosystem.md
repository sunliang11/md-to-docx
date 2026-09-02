# P4 — Ecosystem：标准、市场、Cloud、AI Editing（v4.0）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P3B `DONE`。没有真实第三方模板/插件需求时，**不要实施本 plan 的 Marketplace 与 Cloud。** 先做 Task 0 门闩。
> **Depends on:** P3B
> **Target version:** `4.0.0`

---

## Execution contract

### Goal

让别人给 md-to-docx 提交模板、插件和集成；DOCX 仍是第一公民；核心引擎继续开源。10k star 是生态结果，不是本 plan 的验收项。

### 禁止

- 把核心转换引擎闭源去做 SaaS
- 引擎绑定单一 AI 供应商
- 变成万能 PDF/HTML/PPT 工厂（HTML/PDF renderer 可以有，但不得拖垮 DOCX 质量）
- 未出现真实插件作者就做支付、评分、推荐算法
- 过度设计 Document Standard 的 50 个 container

### Done when（分闸，允许只完成 Gate A）

Gate A 必须：Document Markdown Spec 文档化 + 模板贡献流程（PR 到 `templates/`）。

Gate B 有 3 个外部模板 PR 或 2 个外部插件后再做：静态 Marketplace 页。

Gate C 有稳定流量后再做：Cloud API（开源引擎 + 可选托管）。

Gate D：AI Document Editing（DOCX→AST→MD→AI→MD→AST→DOCX）且 AI 在外围。

Agent 一次只做 **一个 Gate**。做完停下。

---

## Task 0 — 门闩（每次开 P4 先跑）

在 Execution log 写证据：

1. GitHub 是否已有外部 contributor 提交模板或插件？issue 数量？
2. Monthly documents generated 有没有粗测（CLI `--telemetry` 默认关，不要偷偷上报）
3. 若没有任何外部需求：只允许做 Gate A 的 spec 文档，然后 **STOP**

没有证据就做 Cloud = 失败。

---

## Gate A — Open Document Markdown Spec + 模板贡献

### A.1 Spec 文档

新建 `spec/document-markdown.md`（版本 `odm-0.1`）：

锁定已实现语法（不要发明未实现的）：

- CommonMark + GFM
- YAML frontmatter 字段表：`title author date template toc numbering preset`
- `<!-- pagebreak -->` 与 `:::pagebreak`
- `![alt](src){#fig:id}`、`Table: caption {#tbl:id}`、`[@fig:id]`
- `$math$` `$$math$$`
- ` ```mermaid `
- footnotes
- 明确 **非目标：** 任意 HTML、自定义 XML

`:::warning` 仅当已有 renderer 支持 callout。**P4 之前没做就不要写进 spec。** 若要做 callout：先一个 Task 实现 `:::warning|info|note` 三个，再写进 spec。锁定：Gate A 可以加这三个 callout（AST `Callout` 节点 + 渲染为带底色的表格或段落）。这是「标准」该有的最小扩展。

### A.2 Callout 实现（仅三个）

Parser container → `Callout(kind, children)`。Renderer：左边框颜色。测试三份。

### A.3 模板贡献

```
templates/
  README.md                 # 命名、预览图、license、PR 要求
  technical-design/
  mckinsey-like-report/     # 命名不要侵权：用 `consulting-report`
  ieee-like-paper/          # 用 `academic-ieee-ish` 或 `conference-paper`
  chinese-official/
```

每个模板：`template.docx`、`preview.png`、`sample.md`、`LICENSE`（必须允许再分发）。PR 模板 checklist：Word 打开、CJK、无宏、无嵌入个人信息。

CI：对 `templates/**/sample.md` `--template` 转换成功。

根 README Marketplace 暂时就是这个目录。

### A.4 PDF/HTML renderer — **不做完整产品**

允许实验目录 `scripts/md_to_docx/render/html.py` 把 AST 打成简单 HTML（Playground 预览可改走它）。**禁止** 本 Gate 做 PDF（weasyprint/prince 依赖地狱）。PDF 另开 plan。

验收：spec 文件存在、callout 测试绿、至少一个新社区模板目录（即使是官方示例）。

---

## Gate B — 静态 Marketplace

仅当 Task 0 证明有外部贡献。

- GitHub Pages 或 `marketplace/` 静态站：列出 `templates/` 与 `examples/plugins/`
- 每卡片：截图、作者、license、安装（clone 路径）
- 无账号、无上传 API、合并走 GitHub PR
- Plugin 列表同样

不要自建用户系统。

---

## Gate C — Cloud API

仅当自托管 Docker 已有真实用户喊「不想跑 Docker」。

原则：

- 同一 FastAPI 从 P2B 抽 `packages/server`
- 鉴权：先 API token 文件，不做社交登录
- 计费：本 Gate **不做**
- SLA：文档写 best-effort
- 核心 `scripts/md_to_docx` 继续 MIT
- README 大字：Self-host is first-class

实现：`POST /v1/convert` multipart，返回 docx。OpenAPI 生成。SDK **先不出**，curl 示例足够。

安全：与 P2B 相同限额；malware 扫描不做（docx 是我们生成的）。上传 md 扫描过大。

**禁止** 把用户文档用于训练。隐私政策一页 markdown。

---

## Gate D — AI Document Editing

外围流程，引擎不调模型：

```
md-to-docx reverse report.docx -o report.md
# 用户/Agent 编辑 report.md（任意模型）
md-to-docx convert report.md --template original.docx -o report-v2.docx
md-to-docx diff report.docx report-v2.docx
```

Skill/MCP 增加 tool：`edit_roundtrip` 说明三步，**仍不内置 API key**。

可选：`--preserve-template` 从原 docx 抽 styles 当 `--template`（P1B 已能吃 docx 模板）。若 reverse 丢掉样式：实现 `extract_template(docx) -> temp.docx`（剥 body 留 styles/header）。这是本 Gate 唯一引擎活。

测试：原 professional 模板色还在 v2。

不要做协同编辑 OT/CRDT。

---

## 多渲染器终局（提醒）

```
AST → DOCX (第一公民)
    → HTML (预览)
    → PDF (未来，独立 plan)
```

任何 PDF 任务不得降低 DOCX 测试黄金件。

---

## 组织拆分（最后才做）

仅当仓库太大：按 aim.md 拆 `md-to-docx-web` 等。本 plan Gate A–D **默认仍 monorepo**。拆仓需要单独 migration plan，不在这里执行 `git filter-repo`。

---

## 验收（Gate A）

```bash
pytest tests/ -v
test -f spec/document-markdown.md
python -m md_to_docx tests/fixtures/callout.md --output-dir /tmp/p4
```

Gate B–D：各自补充 Execution log 证据链后再写子任务落地 PR。

---

## 战略收口（给人类看）

错误路线：无限加 Markdown 方言。  
正确路线：AI → Markdown → Document Compiler → Professional DOCX，入口可以很多，引擎只有一个，且开源。

---

## Execution log

### 2026-09-02 — Task 0 门闩

1. **外部贡献**：`gh` CLI 未认证，无法查询远程 PR/issue。本地仓库无外部模板/插件 PR 记录 → **0 外部模板/插件 PR**。
2. **Monthly documents**：`--telemetry` 未实现；无默认上报 → 无法粗测，符合 plan 要求。
3. **结论**：无外部需求 → **仅执行 Gate A，跳过 Gate B–D**。

### 2026-09-02 — Gate A 验收

```bash
pip install -e ".[dev]"
pytest tests/ -v                    # 全绿
test -f spec/document-markdown.md   # ok
python -m md_to_docx tests/fixtures/callout.md --output-dir /tmp/p4  # ok
pytest tests/test_callout.py tests/test_render_html.py -v  # 10 passed
```

**交付物：**
- `spec/document-markdown.md` (odm-0.1)
- Callout AST + parser + DOCX renderer (`:::warning|info|note`)
- `templates/` 四目录（technical-design, consulting-report, academic-ieee-ish, chinese-official）
- CI `Validate community templates` step
- 实验性 `scripts/md_to_docx/render/html.py`

**未做（按 plan）：** Gate B Marketplace、Gate C Cloud API、Gate D AI Editing。
