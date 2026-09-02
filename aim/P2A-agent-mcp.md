# P2A — Agent Skill 矩阵 + MCP（v2.0 引擎侧）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1D `DONE`（v1.0 引擎稳定）
> **Depends on:** P1D
> **Unblocks:** P2C（扩展要调引擎/MCP）、P3A
> **Target version:** 引擎仍 1.x 或 bump `2.0.0` 仅当有破坏性 CLI 变化。锁定：**本 plan 不破坏 v1 CLI。** MCP 与多 Skill 是加法。版本号：`pyproject.toml` 保持 1.x，除非用户要求 2.0.0。产品里程碑叫 v2.0。

---

## Execution contract

### Goal

任何 AI（ChatGPT / Claude / Gemini / DeepSeek / Cursor / Codex）写出 Markdown 之后，Agent 能一句「转成正式 Word」调 md-to-docx，选 preset，产出 DOCX。MCP 提供同样能力给支持 MCP 的客户端。

### 禁止

- 核心引擎调用 OpenAI/Anthropic API
- 把 Markdown 送到云端再转换（本 plan 全部本地）
- 重写 AST
- 做浏览器插件（P2C）或 Web UI（P2B）
- 「智能改写第三章」——那是 P4 AI Document Editing

### Done when

- [ ] Cursor Skill 仍可用，且描述变成 AI → professional DOCX
- [ ] 增加 Claude Code / Codex 可用的 skill 文件（同一仓库，路径见下）
- [ ] `md-to-docx-mcp` 以 **本仓库内包** 提供（暂不拆独立 git repo）
- [ ] MCP tools：`convert_markdown` `apply_template` `validate_document` `list_presets`
- [ ] 工具描述写清：输入是 Markdown 路径或内容，输出是本地 docx 路径
- [ ] 无 API key 环境变量出现在引擎或 MCP 代码里

---

## 锁定决策

1. **AI 只是入口。** MCP/Skill 只调用 `md_to_docx.engine` 的 Python API 或 subprocess CLI。不要复制转换逻辑。
2. **先不拆 GitHub org 多仓库。** aim.md 的 `md-to-docx-mcp` 目录先放：

```
mcp/
  README.md
  pyproject.toml          # 可选：若用同一 monorepo extra 则省略
  server.py
```

或包内 `scripts/md_to_docx/mcp_server.py`。锁定：**`scripts/md_to_docx/mcp/server.py` + extra `[mcp]`**。用户 `pip install .[mcp]`。

3. **MCP 依赖：** `mcp>=1.0`（官方 Python SDK）。stdio transport。
4. **Skill 矩阵：** 不写 6 份重复 SKILL。一份 `SKILL.md` + `skills/` 薄包装：

```
SKILL.md                      # Cursor（已有）
skills/claude-code/SKILL.md   # 指向同一 CLI
skills/codex/SKILL.md
skills/gemini-cli/README.md   # 若 Gemini CLI 无统一 skill 格式，写 GEMINI.md 片段
```

每个薄文件 ≤ 80 行，命令统一 `md-to-docx` / `bin/convert`。

5. **MCP tools 输入输出（JSON schema 锁定）**

`convert_markdown`

```json
{
  "input_path": "string (optional)",
  "markdown": "string (optional, one of path/markdown required)",
  "output_path": "string (optional)",
  "preset": "string (optional)",
  "template": "string (optional)",
  "toc": "boolean (optional)",
  "engine": "native|pandoc (optional)"
}
```

返回：`{"ok": true, "output_path": "...", "warnings": []}`

`validate_document`：走 P1D `--check` 逻辑，返回 Issue 列表。

`apply_template`：`input_path` + `template` + `output_path`。内部还是 convert。

`list_presets`：无参，返回 preset 名与说明。

`render_preview`：**P2A 不做 HTML 预览**（P2B 的事）。aim.md 列了这个 tool，推迟到 P2B，MCP README 写 `preview: not in 2.0, see web playground`。

6. **安全：** MCP 只写用户指定的 output_path；默认写到输入旁或系统临时目录。拒绝 `output_path` 指向 `/etc` 之类——做 `Path.resolve()` 后必须在 cwd、输入文件父目录、或 `MD_TO_DOCX_OUT` 下。测试覆盖 path jail。

---

## Task 1 — 稳定 Python API（给 Skill/MCP 用）

**新建：** `scripts/md_to_docx/api.py`

```python
def convert(
    source: str | Path,
    *,
    output: Path | None = None,
    preset: str | None = None,
    template: Path | None = None,
    engine: str | None = None,
    toc: bool | None = None,
    markdown_text: str | None = None,
) -> ConvertResult:
    ...
```

`source` 可以是 Path；若 `markdown_text` 提供则写入 temp md 再转。

`ConvertResult`: `output_path`, `warnings: list[str]`, `engine`.

CLI 与 MCP 都调它。**禁止** MCP subprocess 调 CLI（易碎）；允许 Skill 文档告诉 Agent 跑 CLI（Agent 环境更简单）。

测试 `tests/test_api.py`。

---

## Task 2 — MCP server

**新建：** `scripts/md_to_docx/mcp/server.py`、`__main__.py`

入口：`python -m md_to_docx.mcp`

`pyproject.toml`：

```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]

[project.scripts]
md-to-docx-mcp = "md_to_docx.mcp.server:main"
```

README 片段 `references/mcp.md`：Claude Desktop 配置示例：

```json
{
  "mcpServers": {
    "md-to-docx": {
      "command": "md-to-docx-mcp"
    }
  }
}
```

测试：用 mcp SDK 的内存 transport 或直接调 tool 函数（把 handlers 写成纯函数 `handle_convert(args) -> dict`，server 只做注册）。**不要** 用真实 stdio 集成测试卡 CI。

Path jail 单测。

---

## Task 3 — Skill 文档升级

重写根 `SKILL.md`：

- description 含 `AI-generated Markdown`, `professional Word`, `preset technical`
- Agent workflow：
  1. 找 skill-root / 或 PATH 上 `md-to-docx`
  2. 用户若说企微 → `--preset wecom`
  3. 用户若说正式技术方案/设计文档 → `--preset technical --toc --numbering`
  4. 用户若说学术 → academic
  5. 转换后报告输出路径，不改源 md
  6. 含 mermaid 检查 mmdc
- 不要上传企微

薄包装 skills/* 只写「如何安装/symlink」+「执行同一 CLI」。

`references/agents.md`：给 ChatGPT（无 skill 协议）的复制粘贴提示词：说明安装 CLI 后让它输出 md 并给出转换命令，而不是假装 ChatGPT 能跑 MCP。

---

## Task 4 — 错误信息（DX）

所有 MCP error 返回：

```
problem: ...
cause: ...
fix: ...
docs: https://github.com/sunliang11/md-to-docx/blob/main/references/mcp.md
```

CLI 已有 error 风格保持一致。缺 pandoc 且 engine=pandoc 时：fix 写 brew install pandoc。缺 mmdc：fix 写 npm i -g @mermaid-js/mermaid-cli **或** 去掉 mermaid / 用 `--engine native` 当代码块。

测试：故意 missing template，断言 stderr 含 `fix:`。

---

## Task 5 — 文档与 CHANGELOG

README 增加 **Use with AI** 小节（Cursor / Claude Code / MCP），链到 references。强调无 API key。

CHANGELOG Added MCP + multi-skill docs。

---

## 验收命令

```bash
pip install -e ".[mcp,dev]"
pytest tests/ -v
python -m md_to_docx.mcp --help || python -m md_to_docx.mcp --version
python -c "from md_to_docx.api import convert"
```

若 MCP SDK `--help` 立即 stdio 阻塞：`--help` 必须在进入 stdio 前处理。`main()` 先看 argv。

---

## Handoff

P2B 用同一 `api.convert` 做 Web。P2C 浏览器扩展调 Web 或本地。不要在扩展里再实现一份 parser。

---

## Execution log

**2026-09-02** — P2A complete.

```bash
pip install -e ".[mcp,dev,web]"
pytest tests/test_api.py tests/test_mcp.py -v   # 13 passed
python -c "from md_to_docx.api import convert"
python -m md_to_docx.mcp --help
```

Delivered: `api.py`, `errors.py`, `mcp/server.py` + handlers, SKILL.md rewrite, `skills/*`, `references/mcp.md`, `references/agents.md`.
