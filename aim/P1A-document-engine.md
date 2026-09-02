# P1A — Document Engine：AST + Parser + DOCX Renderer（v0.2.0）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P0 `DONE`。[`00-INDEX.md`](00-INDEX.md)、[`aim.md`](aim.md)「Phase 1 / Document AST / 技术原则」
> **Depends on:** P0
> **Unblocks:** P1B
> **Target version:** `0.2.0`
> **Estimated scope:** 3–5 days. 这是整个仓库最重要的技术决策落地。

---

## Execution contract

### Goal

把转换管道从「normalize + pandoc 一把梭」改成：

```
Markdown → Parser → Document AST → Transformer → DOCX Renderer
```

pandoc 路径保留为 `--engine pandoc`，用于回归对照和 WeCom 旧行为。默认引擎改为 `native`。

### 禁止

- 在 Parser 里 `from docx import Document` 或任何 python-docx / lxml OOXML
- `if template == "technical":` 这种模板分支（模板是 P1B）
- 实现完整 TOC / Header-Footer / Preset / OMML / Caption（P1B/P1C）
- 删除 pandoc 路径、删除 WeCom Lua filter、删除 `reference-wecom.docx`
- 把包从 `scripts/md_to_docx` 迁到 `src/`
- Web / MCP / 插件 API
- 为「支持所有 Markdown 方言」无限加语法。本阶段只锁定：CommonMark + GFM + 我们列出的少量扩展

### Done when

- [ ] 存在独立 AST 模块，可用 pytest 构造文档树并 roundtrip 打印
- [ ] `python -m md_to_docx x.md` 默认走 native renderer，产出可被 Word 打开的 docx（即合法 ZIP+OOXML）
- [ ] `--engine pandoc` 仍通过现有 `tests/test_docx_output.py` 行为（或显式标记为 pandoc-engine tests）
- [ ] native 引擎有自己的 XML 断言：heading / paragraph / list / table / code / link / quote / image / CJK 字体
- [ ] Parser 文件 `grep -n "docx\|OxmlElement\|qn(" scripts/md_to_docx/parse scripts/md_to_docx/ast` 无匹配

---

## 锁定决策

1. **AST 用 dataclasses，不用 pydantic。** 标准库即可，树节点要可比较（`eq=True`）方便单测。
2. **Parser 用 `markdown-it-py` + `mdit-py-plugins`（GFM / frontmatter / tasklists / dollarmath 先不启用 dollarmath——数学是 P1C）。** 不要用 `pandoc -t json` 当主 parser（那会让 native 引擎仍依赖 pandoc）。
3. **Renderer 用 `python-docx`。** 把它从 `[project.optional-dependencies] dev` 提升到 `[project] dependencies`。
4. **默认 `--engine native`。** `MD_TO_DOCX_ENGINE` env 可覆盖。`pandoc` 仍是合法值。
5. **WeCom：** `--engine pandoc` 保持现有 Lua + reference-wecom 行为，单测不丢。native 引擎用同一套 CJK 字体默认值（微软雅黑 + Consolas），但不跑 Lua。
6. **Normalizer：** 现有 `normalizer.py` 继续作为 parse 前的可选 preprocess，由 `--normalize / --no-normalize` 控制，默认 `on`（兼容当前「修烂 Markdown」价值）。Normalizer 输出仍是 Markdown 字符串，不是 AST。
7. **Mermaid：** native 引擎 P1A **原样保留 fence 为 `CodeBlock(lang="mermaid")`**，不调用 mmdc。P1C 再变成 `Mermaid` 节点 + SVG。pandoc 引擎继续现有 PNG 流程。
8. **版本：** `scripts/md_to_docx/__init__.py` 与 `pyproject.toml` 改为 `0.2.0`。更新 `tests/test_cli.py` 的版本断言，不要写死只接受 `0.1.0`。

---

## 目标包结构（必须按此创建）

```
scripts/md_to_docx/
  __init__.py              # version 0.2.0；可 re-export convert API
  __main__.py              # 不变
  cli.py                   # 加 --engine，转发到 engine
  paths.py                 # 不变
  converter.py             # 拆：保留 pandoc 路径函数；新增 convert() 门面
  normalizer.py            # 不变
  reference.py             # 仍只服务 pandoc reference-wecom
  ast/
    __init__.py            # 导出公共节点类型
    nodes.py               # Document / Block / Inline dataclasses
    visitor.py             # NodeVisitor
  parse/
    __init__.py
    markdown.py            # markdown-it-py → AST
    frontmatter.py         # YAML --- --- 到 Metadata
  render/
    __init__.py
    docx_renderer.py       # AST → python-docx
    styles.py              # 默认样式（字体、代码块底色、表格边框）
  engine/
    __init__.py
    native.py              # normalize? → parse → render
    pandoc.py              # 把现有 convert_one 包装进来
```

不要建空的 `transform/`、`plugin/`。P1B 再加。

---

## AST 规格（锁定，按此实现 `ast/nodes.py`）

全部节点 `@dataclass(frozen=True, slots=True)`。`Inline` 与 `Block` 用 Union 类型别名，不要深继承超过一层。

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Union

Alignment = Literal["left", "center", "right", "default"]

@dataclass(frozen=True, slots=True)
class Text:
    value: str

@dataclass(frozen=True, slots=True)
class Strong:
    children: tuple[Inline, ...]

@dataclass(frozen=True, slots=True)
class Emphasis:
    children: tuple[Inline, ...]

@dataclass(frozen=True, slots=True)
class Strike:
    children: tuple[Inline, ...]

@dataclass(frozen=True, slots=True)
class Code:
    value: str

@dataclass(frozen=True, slots=True)
class Link:
    href: str
    children: tuple[Inline, ...]
    title: str | None = None

@dataclass(frozen=True, slots=True)
class InlineImage:
    src: str
    alt: str = ""
    title: str | None = None

@dataclass(frozen=True, slots=True)
class Break:
    """Hard line break."""

@dataclass(frozen=True, slots=True)
class SoftBreak:
    pass

Inline = Union[
    Text, Strong, Emphasis, Strike, Code, Link, InlineImage, Break, SoftBreak
]

@dataclass(frozen=True, slots=True)
class Heading:
    level: int  # 1-6
    children: tuple[Inline, ...]
    anchor: str | None = None

@dataclass(frozen=True, slots=True)
class Paragraph:
    children: tuple[Inline, ...]

@dataclass(frozen=True, slots=True)
class ListItem:
    children: tuple[Block, ...]
    checked: bool | None = None  # None=not a task; True/False=task

@dataclass(frozen=True, slots=True)
class ListBlock:
    ordered: bool
    items: tuple[ListItem, ...]
    start: int = 1
    tight: bool = True

@dataclass(frozen=True, slots=True)
class TableCell:
    children: tuple[Block, ...]
    align: Alignment = "default"
    header: bool = False

@dataclass(frozen=True, slots=True)
class Table:
    rows: tuple[tuple[TableCell, ...], ...]
    # rows[0] is header if any(cell.header for cell in rows[0])

@dataclass(frozen=True, slots=True)
class CodeBlock:
    text: str
    lang: str | None = None

@dataclass(frozen=True, slots=True)
class BlockQuote:
    children: tuple[Block, ...]

@dataclass(frozen=True, slots=True)
class ThematicBreak:
    pass

@dataclass(frozen=True, slots=True)
class Image:
    src: str
    alt: str = ""
    title: str | None = None

@dataclass(frozen=True, slots=True)
class PageBreak:
    pass

@dataclass(frozen=True, slots=True)
class HTMLBlock:
    """Passthrough; renderer ignores or dumps as text in P1A."""
    raw: str

Block = Union[
    Heading, Paragraph, ListBlock, Table, CodeBlock, BlockQuote,
    ThematicBreak, Image, PageBreak, HTMLBlock,
]

@dataclass(frozen=True, slots=True)
class Metadata:
    title: str | None = None
    author: str | None = None
    date: str | None = None
    extra: tuple[tuple[str, str], ...] = ()

@dataclass(frozen=True, slots=True)
class Document:
    blocks: tuple[Block, ...]
    metadata: Metadata = field(default_factory=Metadata)
```

`PageBreak` 的 Markdown 语法在 P1A 就要解析（便宜且 aim.md 已指定）：

- 单独一行 `<!-- pagebreak -->`
- 单独一块 `:::pagebreak` + `:::`（container，可用 markdown-it container 插件；若插件成本高，P1A 只实现 HTML comment，container 留 P1B）

**P1A 锁定 pagebreak：只实现 HTML comment。** `:::pagebreak` 在 P1B。

`Image` vs `InlineImage`：GFM 里独立一段只有一张图 → `Image` block；段落内 → `InlineImage`。Renderer：block image 单独成段居中可选，P1A 左对齐即可。

Visitor：

```python
class NodeVisitor:
    def visit(self, node): ...
    def generic_visit(self, node): ...
```

用 `functools.singledispatchmethod` 或 `visit_Heading` 命名约定。单测：数一棵树里 Heading 个数。

---

## Task 1 — 依赖与版本

**文件：** `pyproject.toml`、`scripts/md_to_docx/__init__.py`、`CHANGELOG.md`、`tests/test_cli.py`

主依赖改为：

```toml
dependencies = [
  "markdown-it-py>=3.0",
  "mdit-py-plugins>=0.4",
  "python-docx>=1.0",
]
```

`dev` 仍含 `pytest` `lxml`。`python-docx` 可从 dev 去掉（已在主依赖）。

`requires-python` 保持 `>=3.10`。

版本 `0.2.0`。

`test_cli.py`：`assert "0.2.0" in result.stdout or ...` 改为从 `md_to_docx.__version__` 读取，避免下次再改测试。

验收：

```bash
pip install -e ".[dev]"
python -c "import markdown_it, docx; from md_to_docx import __version__; print(__version__)"
```

---

## Task 2 — AST 节点 + visitor + 单测

**新建：** `scripts/md_to_docx/ast/nodes.py`、`visitor.py`、`__init__.py`

**新建测试：** `tests/test_ast.py`

测试必须覆盖：

1. 构造一棵含 Heading/Paragraph/List/Table/CodeBlock 的 Document，`==` 相等
2. frozen：`doc.blocks = ()` 应 raise
3. visitor 收集所有 `Text.value`
4. 非法 heading level：在 `__post_init__` 里 `Heading` 断言 `1 <= level <= 6`

不要在 AST 模块 import parser 或 renderer。

验收：`pytest tests/test_ast.py -v`

---

## Task 3 — Frontmatter + Markdown parser

**新建：** `parse/frontmatter.py`、`parse/markdown.py`

### 3.1 Frontmatter

识别文件开头：

```
---
title: X
author: Y
---
```

用标准库 `yaml` 会多一个依赖。P1A **不要加 PyYAML**。手写一个极小解析：只支持顶层 `key: value` 单行，值去引号。无法解析则 `extra` 忽略坏行并 warning 到 stderr，不要 crash。

返回 `(Metadata, remaining_markdown: str)`。无 frontmatter 则 Metadata 全 None，原文不动。

测试：`tests/test_parse_frontmatter.py`

### 3.2 markdown-it-py 配置

```python
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin  # 若与手写冲突，不用这个插件
from mdit_py_plugins.tasklists import tasklists_plugin
from mdit_py_plugins.strikethrough import strikethrough_plugin  # 若 GFM 已含则不要重复
```

实际以 `MarkdownIt("gfm-like")` 或 `MarkdownIt("commonmark").enable("table").enable("strikethrough")` 为准。实现时读 markdown-it-py 文档，**启用：table, strikethrough, linkify 不要启用（避免把代码里 URL 乱变链接）**。

`md.parse(src)` 得到 token 流，写 `tokens_to_document(tokens) -> Document`。

映射表（必须实现）：

| Token | AST |
|-------|-----|
| heading_open/close | Heading |
| paragraph_open/close | Paragraph |
| bullet_list / ordered_list | ListBlock |
| list_item | ListItem |
| fence | CodeBlock（info string → lang） |
| code_block | CodeBlock(lang=None) |
| blockquote | BlockQuote |
| table | Table + TableCell |
| hr | ThematicBreak |
| html_block 含 `<!-- pagebreak -->` | PageBreak |
| image（block） | Image |
| inline: text, strong, em, s, code_inline, link, image, hardbreak, softbreak | 对应 Inline |
| task list token | ListItem.checked |

未识别的 block：降级为 `Paragraph([Text(raw)])` 或 `HTMLBlock`，并在 `warnings` 列表返回。不要 silent drop。

### 3.3 公共 API

```python
def parse_markdown(text: str, *, source_path: Path | None = None) -> Document:
    ...
```

`source_path` 仅用于解析相对图片路径（存 Metadata.extra 或让 Image.src 保持相对，renderer 用 source_path.parent 去找文件）。**Image.src 保持 Markdown 里的相对路径字符串，不要在 parser 里读文件。**

### 3.4 测试 `tests/test_parse_markdown.py`

用字符串夹具，不断言 docx。至少：

- `# H1` → Heading(1)
- 段落 + **bold** + `code`
- 有序/无序/嵌套 list
- GFM table 3x2
- fenced python code
- blockquote
- `<!-- pagebreak -->`
- task list `- [x] a`
- 中文标题与段落
- 图片 `![alt](./x.png)`
- 空文档 → `Document(blocks=())`

验收：`pytest tests/test_parse_markdown.py tests/test_parse_frontmatter.py -v`

---

## Task 4 — DOCX renderer（无 TOC、无页眉）

**新建：** `render/styles.py`、`render/docx_renderer.py`

### 4.1 默认样式（`styles.py`）

从 `reference.py` 抄字体常量，不要 import `reference.py`（它依赖重建模板的副作用风格）：

```python
BODY_FONT_LATIN = "Calibri"
BODY_FONT_EAST_ASIA = "Microsoft YaHei"
MONO_FONT = "Consolas"
CODE_FILL = "F5F5F5"  # RGB hex
HEADING_SIZES_PT = {1: 22, 2: 18, 3: 16, 4: 14, 5: 12, 6: 12}
BODY_SIZE_PT = 11
CODE_SIZE_PT = 9
```

`configure_document_styles(doc: Document) -> None`：

- Normal：拉丁 Calibri，东亚 微软雅黑，11pt，行距 1.15
- Heading 1–6：加粗，对应字号，东亚雅黑
- 自定义段落样式 `MDCodeBlock`：Consolas 9pt，底纹 `F5F5F5`，段前段后 6pt
- 表格：全框线 `w:tblBorders` 单线 4pt 色 `BFBFBF`
- themeFontLang：en-US + zh-CN（复制 `reference.py` 的 `set_theme_font_lang`）

### 4.2 Renderer API

```python
def render_docx(document: ast.Document, out_path: Path, *, base_dir: Path | None = None) -> None:
    ...
```

- `base_dir` 用于解析 `Image.src`
- 图片文件不存在：插入 alt 文本段落 `[missing image: ...]`，stderr warning，不要抛异常导致整篇失败
- `PageBreak`：`doc.add_page_break()`
- `CodeBlock`：按行 `add_paragraph`，样式 `MDCodeBlock`；**P1A 不做行号、不做语法高亮着色**
- `Table`：`doc.add_table(rows, cols)`；header 行 bold + 底纹 `E7E6E6`
- `ListBlock`：用 Word 列表（`paragraph.style = List Number / List Bullet`）。嵌套 list：通过 `paragraph._p.get_or_add_pPr()` 的 `ilvl` 设置层级（0–8）。参考 python-docx 列表操作；写一个 `_apply_list_level(paragraph, ordered: bool, level: int)` 辅助函数
- `Link`：`run.font.color` 蓝色 + underline；`r.hyperlink` 用 python-docx 的 `paragraph.add_run` + relationship。若实现成本高：P1A 允许写成蓝色下划线文本 + 括号 URL `text (https://...)`，但必须在 `render/docx_renderer.py` 顶部注释 `TODO P1B: native hyperlink relationship`。**优先真 hyperlink。** 参考：`docx.oxml` hyperlink 示例，搜 python-docx add hyperlink helper——很多项目复制同一 20 行函数，把它放进 `render/docx_renderer.py` 的 `_add_hyperlink`
- `Strike`：`run.font.strike = True`
- `BlockQuote`：左缩进 0.5 inch，字体色 `#595959`，可选左侧不做 bar（P1A 不做 OOXML border 也行）
- `ThematicBreak`：底边框段落
- Metadata.title：若存在，且文档第一个 block 不是 H1，则先插入 H1。若第一个已是 H1，不重复
- 中文：不要给每个 run 手动设 eastAsia，靠 style 的 rFonts eastAsia

超宽表：P1A 设 `tblW` type=pct 5000（100%）。单元格允许换行。合并单元格 **不做**（Markdown 也没有 colspan）。

### 4.3 测试 `tests/test_native_docx.py`

模式对齐 `tests/test_docx_output.py`：zipfile + lxml xpath。

夹具：把 `tests/fixtures/sample.md` 和 `tests/fixtures/comprehensive.md` 用 native 引擎转换到 tmp。

断言：

- `[Content_Types].xml` 存在（合法 docx）
- 至少一个 `w:pStyle w:val="Heading1"` 或 Heading2（视夹具而定）
- 存在 `w:tbl`
- 代码段落使用 `MDCodeBlock` 或 Consolas `w:rFonts`
- 东亚字体 `w:eastAsia="Microsoft YaHei"` 出现在 styles 或 runs
- comprehensive 的中文「综合测试」出现在 `w:t`
- pagebreak 夹具：`w:br w:type="page"`

不要复制 pandoc 引擎对 Lua 特有样式名的断言。

验收：`pytest tests/test_native_docx.py -v`

---

## Task 5 — Engine 门面 + CLI

### 5.1 `engine/native.py`

```python
def convert_native(md_path: Path, out_docx: Path, *, normalize: bool = True) -> None:
    text = md_path.read_text(encoding="utf-8")
    if normalize:
        from md_to_docx.converter import normalize_md
        text = normalize_md(text)
    doc = parse_markdown(text, source_path=md_path)
    render_docx(doc, out_docx, base_dir=md_path.parent)
```

### 5.2 `engine/pandoc.py`

把 `converter.convert_one` 原样调用。**不要复制 400 行。** `convert_one` 签名保持。

### 5.3 `converter.py` 增加门面

```python
def convert_file(md_path: Path, out_docx: Path, *, engine: str = "native", **pandoc_kwargs) -> None:
    if engine == "native":
        convert_native(md_path, out_docx)
    elif engine == "pandoc":
        convert_one(...)  # 现有参数
    else:
        raise ValueError(...)
```

CLI 批量循环改走 `convert_file`。

### 5.4 CLI flags

```
--engine {native,pandoc}   default native
--normalize / --no-normalize
```

env：`MD_TO_DOCX_ENGINE=pandoc` 在 flag 缺省时生效。flag 优先于 env。

`--help` 文案改成 document compiler，不要只写 WeCom。

### 5.5 pandoc 引擎测试隔离

现有 `tests/test_docx_output.py`、`tests/test_cli.py` 里真正调用转换的测试：

- 明确走 `--engine pandoc` **或** 在测试里调用 `convert_one`（已经如此的保持）
- 新增 CLI 测试：默认引擎 native 转换 `sample.md` 成功
- `test_version_flag` 用 `__version__`

### 5.6 无 pandoc 时 native 必须能跑

加测试 `tests/test_native_no_pandoc.py`：monkeypatch `shutil.which` 让 `pandoc` 不存在，调用 native convert，应成功。这是 native 引擎的关键价值。

验收：

```bash
pytest tests/ -v
python -m md_to_docx tests/fixtures/sample.md --output-dir /tmp/p1a --engine native
python -m md_to_docx tests/fixtures/sample.md --output-dir /tmp/p1a-p --engine pandoc
```

两条都产生 docx。

---

## Task 6 — 文档与 examples

- `README.md` / `README.zh.md`：Quick Start 注明默认 native，无需 pandoc；Mermaid 仍需 mmdc **仅 pandoc 引擎**。诚实写：native 的 mermaid 本版本当代码块展示。
- `references/development.md`：画新管道图；说明双引擎
- `CONTRIBUTING.md`：新包结构
- `CHANGELOG.md`：`## [0.2.0]` Added AST/parser/native renderer；Changed default engine
- `examples/README.md`：去掉「only pandoc pipeline」过时句
- `SKILL.md`：默认命令仍 `bin/convert`；加一句 native 默认、企微如需旧排版用 `--engine pandoc`

`references/wecom-import.md`：第一句改为推荐 `--engine pandoc` 以保持现有企微 Lua 布局。

---

## Task 7 — CI

`.github/workflows/ci.yml`：

- native 转换 examples **不安装 pandoc 的 job**（新 job `test-native`）：只 setup python，不 apt pandoc，跑 `pytest tests/test_ast.py tests/test_parse_markdown.py tests/test_native_docx.py tests/test_native_no_pandoc.py`
- 原 job 继续装 pandoc，跑全量（含 pandoc 引擎）

matrix 3.10–3.12 保持。

---

## 架构禁区自检（合并前必跑）

```bash
# Parser/AST 不得依赖 python-docx
python3 - <<'PY'
from pathlib import Path
bad = []
for p in Path("scripts/md_to_docx/ast").rglob("*.py"):
    t = p.read_text()
    if "docx" in t or "OxmlElement" in t:
        bad.append(p)
for p in Path("scripts/md_to_docx/parse").rglob("*.py"):
    t = p.read_text()
    if "docx" in t or "OxmlElement" in t:
        bad.append(p)
print(bad)
raise SystemExit(1 if bad else 0)
PY
```

---

## 明确不做（P1B+）

| 能力 | 去向 |
|------|------|
| `--template` / style definition 文件 | P1B |
| Word 原生 TOC field | P1B |
| Header/Footer/页码 | P1B |
| `:::pagebreak` container | P1B |
| Mermaid → SVG | P1C |
| Math OMML | P1C |
| Caption / Cross-ref | P1C |
| `--preset` | P1D |
| 语法高亮 / 代码行号 | P1C 或更后，不要在 P1A 做 |

---

## Handoff to P1B

P1B 将在 AST 上加 Transformer（编号、TOC 收集）和 Template（从 docx 参考文档读样式，而不是 if 模板名）。不要在 P1A 把样式硬编码成「technical vs academic」分支——只允许一套 DefaultTheme 常量。

---

## Execution log

**2026-09-02** — P1A done. v0.2.0→1.0.0 shipped in combined session. AST/parser/native renderer; pytest 92 passed.
