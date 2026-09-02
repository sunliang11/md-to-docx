# P3B — VS Code、Obsidian、最小 Plugin API（v3.5）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P3A `DONE`（AST + CLI convert/reverse 稳定）
> **Depends on:** P3A
> **Unblocks:** P4
> **Target version:** 编辑器扩展各自 `0.1.0`；引擎 bump `1.x` 或 `3.5.0` 仅当 Plugin API 进入主包。

---

## Execution contract

### Goal

开发者在熟悉的编辑器里一键导出 Word；第三方能写**真实需要的**插件（先内部把 Mermaid/Math 迁到 plugin 接口，证明 API 不是空想）。

### 禁止

- 100 个接口、SPI、OSGi、复杂生命周期
- 没先有第二个真实插件就抽象 Marketplace
- 在 VS Code 里用 JS 重写转换器
- Obsidian 收费插件商店作为本阶段目标

### Done when

- [ ] VS Code：右键 `Export Markdown to Word` + 命令面板 `MD: Export to DOCX`
- [ ] Obsidian：命令 `Export to Professional Word`
- [ ] Python `Plugin` 协议：`name`, `transform(document) -> document`，可选 `parse_fence(lang, text)`
- [ ] 内置 mermaid 与 math 改为通过该协议注册（行为与 P1C 兼容）
- [ ] 第三方插件：文档示例 `uppercase_headings` 10 行
- [ ] 仍无插件市场网站

---

## 锁定决策

1. **编辑器扩展只 spawn CLI 或调用本机 `md-to-docx`。** 检测 PATH；没有则提示 pip/clone。不要把整个 Python 打进 VSIX。
2. **VS Code 目录：** `editors/vscode/`（本仓库）。`package.json` 命令 `md-to-docx.export`。输出旁路同名 docx 或 `out/` 配置项。
3. **Obsidian 目录：** `editors/obsidian/`。使用 Obsidian plugin API `Notice` + `exec`。桌面端 only；移动端显示不支持。
4. **Plugin API 极小：**

```python
class Plugin(Protocol):
    name: str
    def transform(self, document: Document) -> Document:
        return document

@dataclass
class PluginContext:
    base_dir: Path
    config: dict[str, object]
```

加载：`--plugin path/to/mod.py` 多次。入口 `plugin = Plugin()` 或模块级 `class` 发现。**不**做 setuptools entry_points 扫描（可在 P4 加）。先显式 CLI。

5. **先有真实需求再抽象：** 把 P1C mermaid/math 迁到 `scripts/md_to_docx/plugins/mermaid.py` 与 `math.py`，默认 enabled。证明 transform 钩子够用。不要为图表再发明 Renderer 插件接口，除非 transform 不够——Mermaid 需要「fence→图文件」副作用：允许 plugin 实现 `render_assets(document, ctx) -> Document` 第二钩子。**最多两个钩子。**

```python
class Plugin(Protocol):
    name: str
    def render_assets(self, document: Document, ctx: PluginContext) -> Document: ...
    def transform(self, document: Document, ctx: PluginContext) -> Document: ...
```

两者都有默认 no-op mixin `PluginBase`。

6. **不拆 GitHub org。** 编辑器扩展先住在主仓库。README 说明未来可迁 `md-to-docx-vscode`。

---

## Task 1 — PluginBase + 加载器 + 迁移 mermaid/math

**新建：** `scripts/md_to_docx/plugin/base.py`、`loader.py`、`builtin.py`

`engine/native.py`：parse 之后 `for p in plugins: doc = p.render_assets(doc, ctx); doc = p.transform(doc, ctx)`。

默认插件列表：mermaid, math, captions（captions 也可当 plugin）。

`--no-plugins` 关掉内置（调试用）。

`--plugin ./my.py` 追加。

测试：uppercase plugin 夹具；`--no-plugins` 时 mermaid 保持 CodeBlock。

文档 `references/plugins.md`：警告不要在 plugin 里 import python-docx。资产渲染可以用文件系统。

---

## Task 2 — VS Code 扩展

`editors/vscode/package.json`：

- activationEvents：`onCommand:md-to-docx.export`
- menus：`editor/context` when `resourceLangId == markdown`
- configuration：`md-to-docx.path`、`md-to-docx.preset`、`md-to-docx.extraArgs`

`extension.ts` 或 JS：`child_process.spawn` CLI，output channel 显示 stderr。成功 `showInformationMessage` 带 Open DOCX（`vscode.env.openExternal`）。

`editors/vscode/README.md`：F5 调试、打包 `vsce package`（不发布市场除非用户要求）。

不要提交 `node_modules`。

根 CI **不**强制编译 VS Code（无 Node 矩阵也可）。扩展 README 写 `npm test` 可选。

---

## Task 3 — Obsidian 插件

`editors/obsidian/main.ts`（或 JS 若要零构建：锁定 **JS 无构建** 减少工具链：`main.js` + `manifest.json`）。

manifest：id `md-to-docx`、version `0.1.0`。

命令：Export current file / Export folder。调用 `md-to-docx`，输出到 vault 同目录或配置的 `docx/`。`.gitignore` 建议用户忽略 docx。

桌面 `require('child_process')`；失败 Notice。

文档：如何把文件夹拷进 `.obsidian/plugins/md-to-docx/`。

---

## Task 4 — 示例第三方插件

`examples/plugins/uppercase_headings.py` + README。CI 用它跑一个 md 证明 `--plugin` 有效。

---

## Task 5 — 文档矩阵

根 README 增加 Editors 表：VS Code / Obsidian / CLI / MCP / Browser。CHANGELOG。

aim.md 产品矩阵仍是未来 org；本阶段 README 写「monorepo folders」。

---

## 验收

```bash
pip install -e ".[dev]"
pytest tests/test_plugin_loader.py -v
python -m md_to_docx tests/fixtures/sample.md --plugin examples/plugins/uppercase_headings.py --output-dir /tmp/p3b
```

VS Code/Obsidian：无 GUI 时至少 `manifest.json`/`package.json` 合法 JSON；Execution log 标明未在 IDE 点击。

---

## Handoff

P4 Marketplace 建立在「显式 plugin 文件 + 模板 docx」之上，不要重做 API。Document Standard 在 P4 冻结语法。

---

## Execution log

- 2026-09-02: P3B implemented — Plugin API, mermaid/math/captions plugins, VS Code + Obsidian extensions, `examples/plugins/uppercase_headings.py`, `references/plugins.md`. VS Code/Obsidian not manually clicked in IDE (manifest/package.json validated in CI).
