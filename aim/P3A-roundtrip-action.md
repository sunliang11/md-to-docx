# P3A — Roundtrip、Document Diff、GitHub Action（v3.0）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1D `DONE`（AST 是唯一真相）。P2A 建议已完成（Action 与 CLI 同 API）。
> **Depends on:** P1D
> **Unblocks:** P3B
> **Target version:** `3.0.0` 仅当 CLI 有破坏性变化；否则 `1.x` 加 subcommands。锁定：**用 subcommands，避免破坏 `md-to-docx file.md`。**

---

## Execution contract

### Goal

文档变成可编程：DOCX 能进 AST/Markdown；两个版本能 diff；Git 里 Markdown 是源，DOCX 是构建产物（GitHub Action）。

### 禁止

- 100 个插件接口（P3B 才最小 API）
- VS Code / Obsidian（P3B）
- 为 diff 引入 electron GUI
- 「AI 改第三章」闭环（P4）
- 声称完美 roundtrip 所有 Word 特性（SmartArt、文本框、宏一律不支持）

### Done when

- [ ] `md-to-docx reverse in.docx -o out.md` 产出可读 Markdown
- [ ] 自产自销黄金件：native 引擎生成的 docx → reverse → parse，关键 block 类型计数误差在阈值内
- [ ] `md-to-docx diff a.md b.md` 与 `diff a.docx b.docx`（先 reverse 再比 AST）
- [ ] GitHub Action `uses: sunliang11/md-to-docx@v3`（实现可先放本仓库 `action/`）
- [ ] 不支持的 OOXML 降级并 warning，不 crash

---

## 锁定决策

1. **Roundtrip 路径：**

```
DOCX → OOXML parse → Document AST → Markdown writer
```

不要 docx→pandoc→md 当默认（质量不可控）。允许 `--engine pandoc` reverse 作 fallback。

2. **DOCX parser 范围（v3 只读这些）：**
   - 段落 styles Heading1–6 / Normal
   - 粗斜体删除线等宽
   - 超链接
   - 表格
   - 图片（抽出 `media/` 写到 `{stem}-media/`）
   - 列表（numPr → ListBlock，尽力）
   - 分页符
   - 脚注（若 P1C 已写）
   - 域 TOC：reverse 时丢掉 TOC 段落，避免目录变成正文垃圾
   - OMML → `$latex$` 尽力；失败则 Unicode/纯文本

3. **Markdown writer：** `scripts/md_to_docx/write/markdown.py`。CommonMark + GFM 表 + fence。PageBreak 写成 `<!-- pagebreak -->`。Figure caption 写成 `![cap](path){#fig:id}`。

4. **Diff：** AST 结构化 diff，不是 git 文本 diff 唯一输出。输出格式：
   - 默认 human text（`+` `-` `~` 段落级）
   - `--format json` 给工具
   - `--format md` 生成 changelog 风格

5. **Action：** Docker 或 composite 跑官方 Python。锁定 **composite + setup-python + pip install 本 action 附带的 wheel 或 pip from git tag**。输入 `input` `preset` `output-dir`。把 docx 当 artifact 的步骤写在 action README 示例，不在 action 里强制 upload。

6. **包结构新增：**

```
scripts/md_to_docx/parse/docx.py
scripts/md_to_docx/write/markdown.py
scripts/md_to_docx/diff/ast_diff.py
action/action.yml
action/README.md
```

---

## Task 1 — DOCX → AST

实现 `parse_docx(path: Path) -> Document`。用 `zipfile` + `lxml`（已有 dev 依赖，升到主依赖若 reverse 是核心——锁定 **lxml 进主依赖**，因为 native renderer 测试已用；runtime reverse 需要它）。

只解析 `word/document.xml` + relationships + `word/media`。styles 用 `w:pStyle` val 映射 heading。

复杂 `w:drawing`：提取 `a:blip` rId。忽略图表。

测试 `tests/test_parse_docx.py`：用 native 渲染 `sample.md` 再 parse 回来，断言：

- heading 文本相同
- 至少一张表
- 代码块文本相同（允许尾换行差异）

---

## Task 2 — AST → Markdown writer

`write_markdown(doc: Document) -> str`

测试：`parse_markdown(write_markdown(parse_markdown(src)))` 对 sample.md **block 类型序列**相同。允许 inline 空白差异。这是 roundtrip 的核心契约。

不要要求字节级 md 不变。

---

## Task 3 — CLI subcommands

保持默认：`md-to-docx [options] PATH` 仍是 convert（argparse subparsers 时：无 subcommand 则 convert，避免破坏）。

实现方式锁定：

```
md-to-docx convert ...   # 与今日默认相同，可省略 convert
md-to-docx reverse in.docx -o out.md
md-to-docx diff a b [--format text|json|md]
md-to-docx check ...     # P1D --check 也可迁到这，但保留 --check flag 别拆掉
```

`diff`：输入可以是 .md 或 .docx（按后缀）。两边都变成 AST 再比。

---

## Task 4 — AST Diff

`diff_documents(a: Document, b: Document) -> list[Change]`

```python
@dataclass
frozen=True
class Change:
    op: Literal["add", "remove", "replace"]
    path: str          # e.g. blocks[3]
    summary: str       # "heading: Architecture"
```

算法：按 block 序列 Myers 或简单 LCS（标准库即可）。不要依赖外部 diff 库除非已有。

Human 输出示例（aim.md）：

```
+ Added architecture
~ Modified section 3
- Removed old solution
```

测试：两份仅 H2 文本不同的 Document。

---

## Task 5 — GitHub Action

`action/action.yml`：

```yaml
name: md-to-docx
description: Compile Markdown to professional DOCX
inputs:
  input:
    required: true
  preset:
    default: technical
  output-dir:
    default: dist/docx
  engine:
    default: native
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - run: pip install "${{ github.action_path }}/.."
      shell: bash
    - run: md-to-docx "${{ inputs.input }}" --preset "${{ inputs.preset }}" --output-dir "${{ inputs.output-dir }}" --engine "${{ inputs.engine }}"
      shell: bash
```

注意：`pip install ..` 在 action 作为子目录时路径要对。用 `github.action_path` 指向 `action/` 则 package root 是 `..`。

示例 workflow 写在 `action/README.md`：

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

根 README 加 Git workflow 一节：md 进 git，docx gitignore 可选。

CI：加 job 用本仓库 action 转换 `examples/meeting-notes/example.md`（`uses: ./action`）。

---

## Task 6 — 文档与限制清单

`references/roundtrip.md`：支持矩阵。明确不支持：文本框、SmartArt、修订模式、宏、嵌入 Excel。

CHANGELOG。SKILL.md 增加 reverse/diff 何时用（用户给了 docx 要改成 md 源）。

---

## 验收命令

```bash
pip install -e ".[dev]"
pytest tests/test_parse_docx.py tests/test_write_markdown.py tests/test_diff.py tests/test_roundtrip.py -v
python -m md_to_docx tests/fixtures/sample.md --output-dir /tmp/p3a
python -m md_to_docx reverse /tmp/p3a/sample.docx -o /tmp/p3a/back.md
python -m md_to_docx diff tests/fixtures/sample.md /tmp/p3a/back.md
```

roundtrip 测试允许 `Change` 列表为空或仅 whitespace。

---

## Handoff

P3B 的 Plugin API 应挂在 parse/transform/render 钩子上。reverse 不要绕过 AST。

---

## Execution log

- 2026-09-02: P3A implemented — `parse/docx.py`, `write/markdown.py`, `diff/ast_diff.py`, CLI `reverse`/`diff`, `action/`, tests, `references/roundtrip.md`.
