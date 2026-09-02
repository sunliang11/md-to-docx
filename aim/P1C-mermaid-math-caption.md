# P1C — Mermaid、Math（OMML）、Caption、交叉引用（v0.4.0）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1B `DONE`
> **Depends on:** P1B
> **Unblocks:** P1D
> **Target version:** `0.4.0`

---

## Execution contract

### Goal

做出与「又一个 pandoc 套壳」拉开差距的能力：Mermaid 进 Word（优先 SVG）、数学公式进 Word 原生 OMML、图/表题注、交叉引用。

### 禁止

- 公式只截图当唯一路径（OMML 失败才允许降级 PNG）
- Mermaid 只走 PNG 且写死 mmdc 为唯一实现（PNG 仅作 fallback）
- Preset 名（P1D）
- Plugin API 抽象（P3B）。本阶段把 Mermaid/Math 做成 **内置 transformer**，函数签名要干净，方便以后抽插件，但不要搞 SPI
- 支持 aim.md 列出的每一种 mermaid 图失败就无限调参。覆盖清单见 Task 1，列外的降级为代码块 + warning

### Done when

- [ ] ` ```mermaid ` 在 native 引擎变成图，优先 SVG
- [ ] `$$...$$` 与 `$...$` 变成 OMML（至少加减乘除、分数、上下标、希腊字母）
- [ ] 独立图片可生成 `Figure N. caption` 并带 bookmark
- [ ] `[fig:id]` 或 `[@fig:id]` 解析为可点击交叉引用（至少变成带 bookmark 的超链接文本 `Figure N`）
- [ ] 无 mermaid-cli 时：行为明确（error 或 skip 策略见锁定决策），不 traceback
- [ ] pytest 覆盖上述；pandoc 引擎回归绿

---

## 锁定决策

1. **Mermaid 渲染顺序：** `mmdc --outputFormat svg` → 得到 SVG → 嵌入 DOCX。若 mmdc 失败或缺失：若存在 `MD_TO_DOCX_MERMAID_PNG=1` 再试 PNG；否则把节点当 `CodeBlock(lang=mermaid)` 并 **stderr warning**，退出码仍 0（单文件不因一张图失败）。CLI `--strict-mermaid` 时缺失 mmdc 则 exit 1。
2. **不要引入独立 Chromium 发行。** 继续用系统 Chrome / `PUPPETEER_EXECUTABLE_PATH` / `MD_TO_DOCX_BROWSER`（已有 `converter.py` 逻辑）。把浏览器发现函数从 `converter.py` 抽到 `md_to_docx/util/browser.py`，pandoc 与 native 共用。
3. **SVG 嵌入：** Word 对 SVG 支持看版本。实现两步：尝试 `word/media/*.svg` + `asvg` content type；若测试环境难以验证，**同时**用 `cairosvg` 或 `Pillow`？cairosvg 依赖 cairo，太重。
   - **锁定：** 优先把 SVG 转成 EMF 不现实。P1C 使用 **PNG 作为 Word 兼容嵌入**，但渲染源是 SVG（mmdc 出 SVG 再 `mmdc` 也可直接出 PNG）。
   - aim.md 写「最好优先 SVG」。执行折中：**mmdc 输出 SVG 存档在 `{stem}mermaid/` 旁路文件，docx 内嵌 PNG（高 scale）** 以保证 Word/WPS/企微都能打开。在 CHANGELOG 写：`source SVG saved next to output; embedded raster for compatibility`。
   - 目录：native 引擎用 `{stem}-media/` 而不是 `{stem}mermaid图片/`（旧目录仅 pandoc 引擎保留，避免破坏现有用户）。
4. **Math：** 依赖 `latex2mathml` + 自写 MathML→OMML，或 `latex2omml` 若有可靠库。锁定实现路径：
   - 加依赖 `latex2mathml>=3.0`
   - 新建 `render/omml.py`：MathML XML → OOXML `m:oMath`（映射 mfrac/msup/msub/mi/mo/mn/msqrt/mrow）
   - 覆盖不了的 LaTeX：降级为等宽文本 `E = mc^2` + warning
5. **Caption：** 独立 `Image` block 若 alt 或 title 非空，渲染为 Figure。计数器全局递增。bookmark 名 `fig-N` 或用户 `{#fig:arch}`。
6. **图片 id 语法（锁定一种，不要三种都做）：**
   ```markdown
   ![系统架构](architecture.png){#fig:arch}
   ```
   Parser 从 alt/title 后的 `{#fig:arch}` 读 id。无 id 则自动 `fig-1`。
7. **交叉引用语法（锁定）：** `[@fig:arch]` → 「Figure 1」。中文文档 `--figure-label 图` 则渲染「图 1」。表格 `{#tbl:x}` / `[@tbl:x]` 同样。Heading 自动 slug，`[@sec:slug]` P1C 做 Section 引用。
8. **Footnote：** aim.md P1 列了 Footnote。P1C **要做基础脚注**：`[^1]` / `[^1]: text`。Renderer 用 Word `w:footnote`。这是专业文档刚需，工作量可控。

---

## AST 扩展（`ast/nodes.py`）

新增（frozen dataclasses）：

```python
@dataclass(frozen=True, slots=True)
class Mermaid:
    source: str
    diagram_hint: str | None = None  # flowchart / sequence / ...

@dataclass(frozen=True, slots=True)
class MathBlock:
    latex: str

@dataclass(frozen=True, slots=True)
class MathInline:  # 加入 Inline union
    latex: str

@dataclass(frozen=True, slots=True)
class Figure:
    image: Image | Mermaid
    caption: str
    identifier: str  # fig:arch
    number: int | None = None  # transformer 填写

@dataclass(frozen=True, slots=True)
class CrossRef:
    kind: Literal["fig", "tbl", "sec"]
    identifier: str  # 不含 kind 前缀或含，解析时规范化成 "fig:arch"

@dataclass(frozen=True, slots=True)
class FootnoteRef:  # Inline
    key: str

@dataclass(frozen=True, slots=True)
class FootnoteDef:  # 可放 Document.footnotes
    key: str
    children: tuple[Block, ...]
```

`Document` 增加 `footnotes: tuple[FootnoteDef, ...] = ()`。

`CodeBlock(lang="mermaid")` 在 transformer `transform/mermaid.py` 里升级为 `Mermaid`。Parser 也可以直接认 fence mermaid。锁定：**parser 直接产出 Mermaid 节点**，少一轮。

Table 增加可选 `identifier: str | None`。语法：表后一行 `{: #tbl:foo}` 太怪。锁定表格 caption：

```markdown
Table: API endpoints {#tbl:api}

| A | B |
```

若 markdown-it 难做，preprocess 识别 `Table: ... {#id}` 紧挨表格上方。

---

## Task 1 — Mermaid

**新建：** `scripts/md_to_docx/transform/mermaid.py`、`scripts/md_to_docx/render/image.py`

抽 `converter.py` 的 mmdc 调用为 `util/mmdc.py`：

```python
def render_mermaid_to_files(source: str, out_svg: Path, *, png: Path | None, scale: float, browser: str | None) -> None:
```

支持图表（mmdc 能渲染即可，测试夹具各一份最小源）：

- flowchart
- sequenceDiagram
- classDiagram
- stateDiagram-v2
- erDiagram
- gantt（最小）
- mindmap（若 mmdc 版本失败：标 xfail 并降级代码块，不要卡死整个 plan）

CLI 复用 env：`MD_TO_DOCX_MERMAID_SCALE`（已有）。

测试：

- `tests/test_parse_mermaid.py`：fence → Mermaid 节点
- `tests/test_render_mermaid.py`：有 mmdc skip-if-missing 的集成测试，docx zip 内 `word/media/` 至少 1 个 png
- 无 mmdc：warning 路径单测（mock）

CI：ubuntu job **不要** 默认装 mermaid-cli（慢）。集成测试 `@pytest.mark.mermaid`，CI 不加这 mark 到默认 pytest。文档写：`pytest -m mermaid` 本地跑。`pytest.ini` 配置：

```toml
markers = mermaid: needs mmdc
```

默认 `addopts` 不要排除，用 `pytestmark skipif not shutil.which("mmdc")`。

---

## Task 2 — Math OMML

**新建：** `parse` 启用 `mdit_py_plugins.dollarmath`（或等价）。

**新建：** `render/omml.py` + `tests/test_omml.py`

最小 LaTeX 矩阵（必须过）：

| 输入 | 期望 |
|------|------|
| `$E=mc^2$` | inline oMath，含 sup |
| `$$\frac{a}{b}$$` | block oMath，m:f 分数 |
| `$\alpha + \beta$` | 希腊字母 |
| `$\sqrt{x}$` | radical |
| `$\sum_{i=1}^n i$` | 允许降级，能过最好 |

docx XML 命名空间：

`xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"`

断言存在 `m:oMath`。

失败路径：`$$$broken` 不要崩，当 Text。

---

## Task 3 — Caption + Bookmark + CrossRef

**新建：** `transform/captions.py`、`transform/xrefs.py`

流程：

1. parse
2. `assign_caption_numbers(doc)` 遍历 Figure/Table 填 number
3. `resolve_xrefs(doc)` 把 `CrossRef` 换成 `Link` 指向 `#_bookmark` 或保留 CrossRef 让 renderer 处理
4. render：Figure 下加段落样式 `Caption`（模板没有就创建），文本 `{label} {n}. {caption}`，bookmark 包住编号

Parser 扩展：

- 图片 `{#fig:id}`
- inline `[@fig:id]` `[@tbl:id]` `[@sec:id]`
- Heading 自动 slug：小写、空格变 `-`、保留中文（不要 strip 中文）

测试 `tests/test_captions.py` `tests/test_xrefs.py`：

- 两张图编号 1、2
- `[@fig:arch]` 文本含 `Figure 1` 或 `图 1`
- document.xml 含 `w:bookmarkStart`

`--figure-label` 默认 `Figure`，`--table-label` 默认 `Table`，`--section-label` 默认 `Section`。

中文例子 `chinese-report` 可在 P1D 再改标签；P1C 加 CLI 即可。

---

## Task 4 — Footnotes

Parser：markdown-it footnotes 插件 `mdit_py_plugins.footnote`。

Renderer：python-docx 对 footnotes 支持弱，需 oxml 操作 `word/footnotes.xml` part。参考现有开源 snippet，放 `render/footnotes.py`。

测试：`[^a]` 定义存在时，docx 里 `word/footnotes.xml` 含注释文本。无定义的 ref：原样文本 `[^a]` + warning。

---

## Task 5 — CLI / 文档 / 版本

版本 `0.4.0`。

README Features 更新：Mermaid、Math、Captions、Cross-refs、Footnotes。诚实写 OMML 覆盖范围与 Word 需较新版本。

CHANGELOG。`examples/technical-report/example.md` **现在**可以加 mermaid fence（P0 故意没加）。更新该例子，README 写需要 mmdc。

SKILL.md：转换含 mermaid 时检查 mmdc；公式不要截图。

---

## 验收命令

```bash
pip install -e ".[dev]"
pytest tests/ -v
python -m md_to_docx tests/fixtures/sample.md --output-dir /tmp/p1c
# 含公式/图的新夹具
python -m md_to_docx tests/fixtures/math.md --output-dir /tmp/p1c
python -m md_to_docx tests/fixtures/captions.md --output-dir /tmp/p1c
```

新建夹具 `tests/fixtures/math.md`、`captions.md`、`footnotes.md`。

Parser/AST 仍禁止 import docx。MathML 转换在 `render/`。

---

## Handoff to P1D

差异化能力已在引擎内。P1D 做 preset 打包、质量闸门、v1.0 发布，不再加新语法。

---

## Execution log

**2026-09-02** — P1C done. Mermaid, OMML math, captions, footnotes in v1.0.0.
