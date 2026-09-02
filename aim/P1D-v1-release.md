# P1D — v1.0 Professional Markdown → DOCX

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1C `DONE`
> **Depends on:** P1C
> **Unblocks:** P2A, P2B
> **Target version:** `1.0.0`

---

## Execution contract

### Goal

把引擎收成一个技术用户愿意每天用的 v1.0：Preset、专业模板、文档校验、回归黄金件、发 GitHub Release。第一座山完成：**DOCX 质量明显好于自己手搓 pandoc / python-docx。**

### 禁止

- Web Playground、MCP、浏览器插件、VS Code（P2/P3）
- 新 Markdown 语法
- 把核心闭源
- 强行占用别人的 PyPI 名 `md-to-docx` 去 upload（会失败或侵权）
- 删除 pandoc 引擎（可标 deprecated，v1.0 仍要能跑 WeCom 路径）

### Done when

- [ ] `--preset professional|technical|academic|business|report|wecom` 可用
- [ ] wecom preset = 现有 pandoc 引擎 + reference-wecom（行为兼容）
- [ ] 其余 preset = native 引擎 + 内置模板 docx
- [ ] `md-to-docx --check file.md` 校验但不写 docx
- [ ] examples 全部用 v1 引擎重生并提交
- [ ] GitHub Release `v1.0.0` 的 workflow 仍可用（P0 已加）
- [ ] 测试含 preset / validate；版本号 1.0.0

---

## 锁定决策

1. **Preset 是「选中一份内置模板 + 一组默认 flag」，不是 if 森林。** 实现为数据：

```python
PRESETS: dict[str, Preset] = {
  "professional": Preset(template="professional.docx", engine="native", toc=True, numbering=False, figure_label="Figure"),
  "technical": Preset(template="technical.docx", engine="native", toc=True, numbering=True),
  "academic": Preset(template="academic.docx", engine="native", toc=True, numbering=True),
  "business": Preset(template="business.docx", engine="native", toc=False),
  "report": Preset(template="report.docx", engine="native", toc=True),
  "wecom": Preset(template=None, engine="pandoc", toc=False),
}
```

CLI 显式 flag 覆盖 preset（`--no-toc` 覆盖 technical 的 toc=True）。

2. **内置模板文件：**

```
assets/presets/professional.docx
assets/presets/technical.docx
assets/presets/academic.docx
assets/presets/business.docx
assets/presets/report.docx
```

用 `reference_native.py` 参数化生成（字体/标题色/页眉默认文案不同），**禁止**五份复制粘贴的生成脚本。一个 `scripts/md_to_docx/presets.py` + 数据表。

差异要肉眼可辨：

| preset | 标题色 | 正文字号 | 页眉 |
|--------|--------|----------|------|
| professional | #111827 | 11 | 空，页码 |
| technical | #1E3A5F | 10.5 | 文档 title |
| academic | #000000 | 12 宋体/Times | 论文题名 |
| business | #1F4E79 | 11 | 公司/title |
| report | #0F172A | 11 | Report / date |

CJK：academic 东亚用宋体 `SimSun`，其余微软雅黑。西文 academic 用 Times New Roman，其余 Calibri。

3. **PyPI 名：** 调查后锁定发布名 **`md2docx-compiler`**（若占用则 `ai-md-to-docx`）。GitHub 仓库名永远 `md-to-docx`。`pyproject.toml` 的 `name` 改成选定的未占用名，console script **保持** `md-to-docx`。

   执行 Task 0：用 `curl -sI https://pypi.org/pypi/md2docx-compiler/json` 检查 404 再写进本文件 Execution log。若占用，试 `md-to-docx-compiler`。**不要**用 `md-to-docx`。

4. **`--check`（Document Validation）：** 解析 + 规则，不渲染。规则：
   - 断链图片
   - 未定义的 `[@fig:]` / footnote
   - heading 从 H1 跳到 H4
   - 空文档
   退出码 1（有 error）/ 0（仅 warning 或干净）。`--check --strict` 时 warning 也变 error。

5. **pandoc 引擎：** `--engine pandoc` 与 `--preset wecom` 保留。README 把 wecom 当场景。Deprecation warning **不要在 1.0 喊**，2.0 再说。

6. **黄金回归：** `tests/goldens/` 存 **XML 规范化后的哈希或关键 xpath 快照**，不要存整份 docx 二进制对比（易碎）。对 `examples/*/example.md` 跑 native+professional，断言 heading 数、table 数、存在 styles。

---

## Task 0 — PyPI 名确认

```bash
for n in md2docx-compiler md-to-docx-compiler ai-md-to-docx; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/${n}/json")
  echo "$n $code"
done
```

404 = 可用。把选中的名字写入 `pyproject.toml` `[project].name`，并在 README Install 写：

```
pip install md2docx-compiler
md-to-docx report.md
```

**1.0 可以暂不 `twine upload`。** 有 GitHub Release 资产即可。Upload 仅当用户明确说「发布到 PyPI」。

---

## Task 1 — Preset 数据与生成器

实现 `scripts/md_to_docx/preset.py`：

```python
@dataclass(frozen=True)
class Preset:
    name: str
    template: str | None
    engine: str
    toc: bool
    numbering: bool
    figure_label: str
    table_label: str
    toc_title: str
```

`load_preset(name) -> Preset` 未知名：

```
error: unknown preset 'foo'
hint: professional, technical, academic, business, report, wecom
```

生成脚本 `python -m md_to_docx.presets_build` 写 5 个 docx。提交二进制。hatch force-include `assets/presets/*.docx`。

---

## Task 2 — CLI 合并 preset 与 flag

解析顺序锁定：

1. 默认 professional 吗？**否。** 默认 = native + `reference-native.docx`，无 toc。避免「没要目录却插 TOC」。
2. `--preset X` 应用 Preset 默认
3. 再应用显式 `--toc` `--template` `--engine` 等覆盖

`--preset wecom` 强制 engine=pandoc，忽略 `--template`（warning）。

`tests/test_preset.py`：mock 或真实短 md。

帮助里 Examples：

```
md-to-docx report.md --preset technical
md-to-docx report.md --preset wecom
```

---

## Task 3 — `--check` 校验器

**新建：** `scripts/md_to_docx/validate.py`

```python
@dataclass
class Issue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    line: int | None = None

def validate_document(doc: Document, *, base_dir: Path) -> list[Issue]:
```

codes 锁定：`empty_document` `heading_skip` `missing_image` `unresolved_xref` `unresolved_footnote` `missing_mermaid_cli`（warning）

CLI `--check` 打印：

```
examples/foo.md:12: error: missing_image: ./nope.png
summary: 1 error, 2 warnings
```

机器可读：`--check --format json` 输出 Issue 列表。

测试 `tests/test_validate.py`。

---

## Task 4 — 质量闸门与 examples 重生

```bash
python -m md_to_docx --preset technical examples/technical-report/example.md
# 每个 examples/* 指定合适 preset（chinese-report → professional + --figure-label 图 --toc-title 目录）
```

更新 `scripts/demo/build_examples.sh` 使用 preset。提交新 docx。

`tests/test_examples_smoke.py`：对每个 example.md native 转换成功、docx > 2KB、含 `w:document`。

把 P0 占位 preview.png 留着，不强制真 Word 截图。README 可注明 screenshots are illustrative。

---

## Task 5 — 文档、Skill、版本、Changelog

- 版本 `1.0.0`，Development Status classifier 改为 `5 - Production/Stable`
- README 第一屏 CTA 增加典型命令 `--preset technical`
- 新文档 `references/presets.md`、`references/validation.md`
- SKILL.md：Agent 默认 `--preset technical` 当用户说「正式技术方案」；企微导入用 `--preset wecom`
- CONTRIBUTING：preset 模板如何重建
- CHANGELOG：`## [1.0.0]` 汇总 0.2–0.4 用户能感知的能力（即使那些版本没单独打 tag，1.0 notes 也要完整）

---

## Task 6 — 发布检查单（代码做完，tag 等用户）

Agent 准备好，**不要擅自 git tag / push / gh release**，除非用户要求。

检查单写入 `references/release.md`：

1. pytest 全绿
2. examples 已重建
3. CHANGELOG 1.0.0 日期
4. 用户执行：`git tag v1.0.0 && git push origin v1.0.0` → P0 的 release.yml 跑

---

## 验收命令

```bash
pip install -e ".[dev]"
pytest tests/ -v
python -m md_to_docx --help | grep -E "preset|check"
python -m md_to_docx --check tests/fixtures/comprehensive.md
python -m md_to_docx tests/fixtures/comprehensive.md --preset technical --output-dir /tmp/p1d
python -m md_to_docx tests/fixtures/sample.md --preset wecom --output-dir /tmp/p1d-wecom
```

wecom 路径需要 pandoc。

---

## 第一座山完成标准（写进 README Status）

```
Status: 1.0 — Professional Markdown → DOCX
Default engine: native Document AST
WeCom import: --preset wecom
```

---

## Handoff

下一座山是 AI 入口（P2A Skill/MCP）和 30 秒体验（P2B Web）。引擎不要在 P2 再拆。P2 只包一层。

---

## Execution log

**2026-09-02** — P1D done. v1.0.0, presets, --check, md2docx-compiler package name. PyPI upload not performed.
