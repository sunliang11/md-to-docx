# P1B — Template、TOC、页眉页脚、CJK（v0.3.0）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1A `DONE`（native AST 管道已是默认引擎）
> **Depends on:** P1A
> **Unblocks:** P1C
> **Target version:** `0.3.0`

---

## Execution contract

### Goal

让 native 引擎产出「像正式文档」的 Word：用户可提供参考模板 docx；能插入 Word 原生 TOC；有页眉页脚页码；CJK 混排、表格、分页在 Word 里不崩。

### 禁止

- `if template == "technical":` / `if preset == "academic":`（Preset 是 P1D）
- 在 Parser 里碰 python-docx
- 实现 OMML、Caption 自动编号、Mermaid SVG（P1C）
- 插件系统 / Marketplace
- 为 100 种 Markdown 方言扩展 parser

### Done when

- [ ] `md-to-docx report.md --template path/to.docx` 使用该文件的 styles + header/footer 作为基底
- [ ] `--toc` 写入 Word 原生 TOC field（不是静态纯文本目录）
- [ ] 默认页脚含页码；`--title` / `--author` 可进页眉
- [ ] `:::pagebreak` 与 `<!-- pagebreak -->` 都变成 `PageBreak`
- [ ] CJK 夹具（中英、中文+代码、中文表）XML 断言 + 人工检查清单
- [ ] pytest 全绿；pandoc 引擎不被破坏

---

## 锁定决策

1. **Template = 一份 .docx 参考文档，不是 Python if。** 实现：复制模板 ZIP 为输出起点，或 `Document(template_path)` 然后清空 body 再按 AST 渲染进同一 Document（保留 styles.xml、header、footer、theme）。
2. **无 `--template` 时：** 使用内置 `assets/reference-native.docx`（本阶段新建，由脚本生成，类似现在的 `reference-wecom.docx`，但服务 native 引擎）。
3. **不要复用 `reference-wecom.docx` 当 native 默认模板**（它为 pandoc 样式名服务）。WeCom 继续走 `--engine pandoc`。
4. **TOC：** OOXML `w:fldChar` + `instrText` = `TOC \o "1-3" \h \z \u`。打开 Word 时可能要「更新域」。在 README 写明。额外生成一个静态目录段落作为 fallback **不要做**——只做原生域。
5. **页码：** 页脚 `PAGE` field。
6. **`--title` `--author` `--date`：** CLI 覆盖 frontmatter；写入 metadata 并进页眉（左 title，右 date 或 author）。
7. **编号标题：** `--numbering` 给 Heading 加 `1 / 1.1 / 1.1.1` 前缀文本（真 Word 多级列表映射可做，但 P1B 先做可见前缀 + outline level）。P1D 再考虑 `w:numPr` 多级列表。

---

## 目标新增文件

```
scripts/md_to_docx/transform/__init__.py
scripts/md_to_docx/transform/numbering.py
scripts/md_to_docx/transform/outline.py
scripts/md_to_docx/render/template.py
scripts/md_to_docx/render/fields.py      # TOC / PAGE / hyperlink helpers
scripts/md_to_docx/render/header_footer.py
scripts/md_to_docx/reference_native.py   # 生成 assets/reference-native.docx
assets/reference-native.docx
assets/templates/README.md               # 说明如何做自己的模板
tests/fixtures/cjk.md
tests/fixtures/pagebreak.md
tests/test_template.py
tests/test_toc.py
tests/test_header_footer.py
tests/test_cjk.py
tests/test_parse_containers.py
```

---

## Task 1 — 解析 `:::pagebreak`

**文件：** `parse/markdown.py`

启用 `mdit_py_plugins.container` 或手写 preprocess：

preprocess 更简单且不引入复杂插件：在 `parse_markdown` 开头，把独立成段的

```
:::pagebreak
:::
```

以及 `::: pagebreak` 变体替换为 `<!-- pagebreak -->`，再走现有 HTML comment 逻辑。

也接受 `:::pagebreak :::` 单行。

测试：`tests/test_parse_containers.py`

不要在 P1B 实现 `:::warning` / `:::figure`（那是 P4 Document Standard）。

---

## Task 2 — 内置 native 参考模板

**新建：** `scripts/md_to_docx/reference_native.py`

用 python-docx 从空白文档配置：

- 页边距 1 inch（或 2.54cm）
- Normal / Heading1–6 / MDCodeBlock（与 P1A styles.py 一致）
- 页脚居中 PAGE 域
- 页眉空（由 CLI 填充）
- 页眉页脚不同 first page：**关闭**（P1B 简单）
- 东亚字体 微软雅黑，西文 Calibri，等宽 Consolas
- A4：`section.page_width = Mm(210)` `page_height = Mm(297)`

生成到 `assets/reference-native.docx`。

`pyproject.toml` hatch `force-include` 加上这个文件，和 wecom 参考一样打进 wheel。

`paths.py`：`native_reference_doc()` 与现有 `bundled_path` 对称。

CLI：`python -m md_to_docx.reference_native` 重建。`references/development.md` 写命令。

**不要**在运行时每次重建；提交二进制 `assets/reference-native.docx`。

验收：脚本可重复生成；文件 > 5KB。

---

## Task 3 — Template 加载器

**新建：** `render/template.py`

```python
def open_document(template_path: Path | None) -> Document:
    path = template_path or bundled_native_reference()
    doc = Document(str(path))
    clear_body(doc)
    return doc
```

`clear_body`：删除 `document.body` 里除 `sectPr` 以外的子元素。必须保留 sectPr（页边距、页眉页脚引用）。实现时用 oxml，写单测：模板带 1 个段落 + header，clear 后段落没了，`doc.sections[0].header` 仍可访问。

Renderer 改为：`render_docx(..., template_path=None)` 内部 `open_document`，不再 `Document()` 空白。

把 P1A `configure_document_styles` 改成：

- 若模板已有 Heading 1 / Normal：不覆盖字号/字体（尊重模板）
- 若缺 `MDCodeBlock`：才添加
- `--force-default-styles` flag 可选，P1B 可以不做，缺省尊重模板

锁定：**尊重模板 styles 是默认。** 内置模板已经含我们的 styles，所以默认路径观感不变。

CLI：

```
--template PATH
```

相对路径相对 cwd。不存在则 stderr `error: template not found: ...` 退出码 2。

测试 `tests/test_template.py`：造一个临时 docx，改 Heading1 为红色 28pt，转换 `# Hello`，断言输出 styles 或 run 里出现该字号/颜色。

---

## Task 4 — TOC 原生域

**新建：** `render/fields.py`

辅助函数：

```python
def add_toc_field(paragraph) -> None:
    # w:r + fldChar begin, instrText 'TOC \o "1-3" \h \z \u', fldChar separate, placeholder text, fldChar end
```

Transformer `transform/outline.py`：若 `toc=True`，在 **第一个 Heading 之前** 插入一个伪节点。

**不要把 TOC 做成 AST 节点也可以**，更干净的是 AST 增加：

```python
@dataclass(frozen=True, slots=True)
class TableOfContents:
    levels: int = 3
```

加进 `Block` Union。Parser 不生产它。`engine/native.py` 在 parse 后：

```python
if toc:
    doc = insert_toc(doc, levels=3)
```

`insert_toc` 放 `transform/outline.py`，返回新 Document（frozen AST，用替换 blocks 元组）。

Renderer 遇到 `TableOfContents`：加 Heading「Contents」或中文「目录」（`--toc-title`，默认 `Contents`；若 metadata/lang 以后再做。P1B：`--toc-title` 默认 `Contents`）。然后 `add_toc_field`。

CLI：`--toc` / `--no-toc`。frontmatter `toc: true` 也开启（frontmatter 解析在 P1A 是弱 YAML：给 `toc` 支持 `true/false/yes/no/1/0`）。

测试 `tests/test_toc.py`：

- 转换含 H1/H2 的 md + `--toc`
- unzip `word/document.xml` 断言 `TOC` 出现在 `w:instrText`
- 无 `--toc` 则无该 instrText

README 说明：用 Word 打开后若目录空白，右键域 → 更新。这是 Word 行为，不要用 LibreOffice 硬要求 TOC 已展开。

---

## Task 5 — 页眉 / 页脚 / 页码 / 文档变量

**新建：** `render/header_footer.py`

```python
def apply_header_footer(
    doc: Document,
    *,
    title: str | None,
    author: str | None,
    date: str | None,
    version: str | None,
    page_numbers: bool = True,
) -> None:
```

规则：

- 页眉：左侧 `title or ""`，右侧 `author` 或 `date`（有 author 显示 author，date 放页脚左）
- 页脚：左 `version`（可空），中 `PAGE`，右空
- `--no-page-numbers` 去掉 PAGE
- 若模板已有页眉内容且用户没传 title/author：**保留模板页眉**
- 若用户传了 title：覆盖页眉

CLI：

```
--title
--author
--date
--doc-version          # 不要叫 --version（已是程序版本）
--no-page-numbers
```

frontmatter 键：`title` `author` `date` `version`（文档版本，映射到 `--doc-version`）。

测试 `tests/test_header_footer.py`：读 `word/header1.xml` 或 `header2.xml`（以实际关系文件为准，测试里扫描 zip 内 `word/header*.xml`）包含 title 字符串；`word/footer*.xml` 含 `PAGE`。

---

## Task 6 — 标题编号 Transformer

**新建：** `transform/numbering.py`

```python
def apply_heading_numbers(doc: Document, *, enabled: bool) -> Document:
```

只改 `Heading.children`，在原 inlines 前插入 `Text("1.1 ")`（注意空格）。层级计数数组 length 6。

CLI `--numbering`。默认 off。

测试：AST 级单测即可（不必 XML）。`# A` `## B` `## C` `# D` → `1 A` / `1.1 B` / `1.2 C` / `2 D`。

---

## Task 7 — CJK 质量

**新建夹具** `tests/fixtures/cjk.md`，必须含：

- 纯中文标题与段落
- 中英混排同一段落
- 中文 + Python 代码块（注释中文）
- 中文宽表（8 列短中文）
- 中文有序「1. 2.」与 Markdown 列表

**新建** `tests/test_cjk.py`：

- 所有中文句子出现在 `w:t`（按句抽取）
- `styles.xml` 或 runs 含 `w:eastAsia="Microsoft YaHei"`
- 表格存在
- 代码样式仍是等宽拉丁字体（Consolas），不要把代码块设成雅黑

`references/development.md` 增加 **CJK 人工验收**（agent 做不到真 Word 打开时，把清单写下，CI 只保证 XML）：

1. Word / WPS 打开不报修复
2. 中文标题不出现方框
3. 表不错列到页外完全不可读（宽表可换行）
4. 代码块中文注释可见

agent：用 `file`/`zipinfo` 确认 docx；XML 断言必须过。

---

## Task 8 — Engine / CLI 接线与版本

`engine/native.py` 管道：

```
read → normalize? → parse → apply_heading_numbers? → insert_toc? → render_docx(template, header/footer)
```

版本 `0.3.0`。CHANGELOG、README flags 表、SKILL.md 增加 `--template --toc --title`。

`./bin/convert` 透传 argv，无需改。

帮助文本给错误示例：

```
error: template not found: ./missing.docx
hint: pass a .docx whose styles/header/footer you want to reuse
```

---

## 验收命令

```bash
pip install -e ".[dev]"
pytest tests/ -v
python -m md_to_docx tests/fixtures/comprehensive.md --toc --numbering --title "CJK Test" --output-dir /tmp/p1b
python -m md_to_docx tests/fixtures/cjk.md --template assets/reference-native.docx --output-dir /tmp/p1b
python -m md_to_docx tests/fixtures/sample.md --engine pandoc --output-dir /tmp/p1b-pandoc
```

自检 AST 仍无 docx import。

---

## Handoff to P1C

样式与域已经稳定。P1C 只加节点类型（Mermaid、Math、Figure/Caption、XRef）和对应 renderer，不要再改模板加载器结构。

---

## Execution log

**2026-09-02** — P1B done as part of v1.0.0 release. Templates, TOC, CJK tests.
