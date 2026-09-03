[English](cli.md) | 中文

# CLI 命令手册

**md-to-docx** 命令行完整参考 — AI 时代的开源文档编译器。

项目概览见 [README.zh.md](../README.zh.md)。安装与排错见 [installation.md](installation.md)。

---

## 常用场景速查

复制即可用的命令，附简短说明。

```bash
# 单文件转 Word（技术报告风格）
md-to-docx report.md --preset technical


# 批量转换整个目录，输出到 dist/docx（保留子目录结构）
md-to-docx ./docs --output-dir ./dist/docx

# 预览会转换哪些文件（不实际写入）
md-to-docx ./docs --dry-run

# 使用自己的 Word 模板（信纸、品牌样式等）
md-to-docx report.md --template letterhead.docx

# 只校验 Markdown，不生成 .docx
md-to-docx report.md --check

# Word 转回 Markdown（默认写到同目录同名 .md）
md-to-docx reverse report.docx
md-to-docx reverse report.docx -o other.md

# 对比两个版本的文档结构（输出类似 changelog）
md-to-docx diff v1.md v2.md --format md

# git clone 后免 pip，直接运行
./bin/convert report.md --preset technical

# pip 安装后，任意目录都能用
pip install -e .
md-to-docx report.md --preset professional
```

---

## 怎么运行命令

多种方式效果相同，按你的环境选一种即可。

| 方式 | 适用场景 | 示例 |
|------|----------|------|
| **`bin/convert`** | git clone 或 Cursor skill；**无需 pip** | `./bin/convert report.md` |
| **`pip install -e .`** | 把 `md-to-docx` 装到 PATH，全局可用 | `md-to-docx report.md` |
| **`pip install -e ".[dev]"`** | 开发 + 跑 pytest | 同上，并安装测试依赖 |
| **`pip install -e ".[mcp]"`** | MCP 客户端（Cursor、Claude Desktop） | 同一 CLI；用 `md-to-docx mcp` 启动 |
| **`pip install "git+https://..."`** | 不 clone 本地仓库，远程安装 | 远程 editable 安装 |
| **`python -m md_to_docx`** | 与 `md-to-docx` 等价；PATH 里没有脚本时可用 | `python3 -m md_to_docx report.md` |
| **`PYTHONPATH=scripts python -m md_to_docx`** | 在源码目录直接跑（CI 常用） | 无需 pip install |

### pip 安装步骤

```bash
git clone https://github.com/sunliang11/md-to-docx.git
cd md-to-docx
pip install -e .              # 基础 CLI：md-to-docx
# 可选扩展：
pip install -e ".[dev]"       # pytest、pillow
pip install -e ".[mcp]"       # MCP 依赖；启动：md-to-docx mcp
pip install -e ".[web]"       # Web Playground 依赖

# 验证安装
which md-to-docx              # 应输出 venv 或 ~/.local/bin 下的路径
md-to-docx --version
```

> **暂未发布 PyPI。** Python 包名 `md2docx-compiler`，唯一命令行名是 **`md-to-docx`**。  
> `pip install -e .` 后 PATH 里只会增加 **`md-to-docx`**。MCP 通过子命令 `md-to-docx mcp` 启动（需安装 `[mcp]` 扩展）。

### 可选：shell alias

如果习惯用短命令、且总是用仓库里的版本，可以在 `.zshrc` 里加 alias：

```bash
# ~/.zshrc
alias md_to_docx="/path/to/md-to-docx/bin/convert"
```

子命令和参数完全一样：`md_to_docx report.md`、`md_to_docx reverse …` 等。

### 环境要求（摘要）

| 组件 | 什么时候需要 |
|------|--------------|
| Python 3.10+ | 始终 |
| mmdc（Mermaid CLI） | 需要把 Mermaid 图渲染成图片 |
| Chrome / Edge / Chromium | Mermaid 渲染（mmdc 依赖浏览器） |

详见 [installation.md](installation.md)。

---

## 命令总览

```
md-to-docx [--version] [convert 选项] PATH     # 默认子命令 = convert（正向编译）
md-to-docx convert [选项] PATH
md-to-docx reverse INPUT [-o OUTPUT]
md-to-docx diff A B [--format text|json|md]
md-to-docx build presets|all         # 开发者：重建模板
```

| 子命令 | 作用 |
|--------|------|
| 默认 / `convert` | Markdown → Word（.docx） |
| `reverse` | Word → Markdown |
| `diff` | 对比两个文档的结构差异（支持 .md 和 .docx） |
| `build` | 重建内置 Word 模板（开发/发版用） |

旧写法 `md-to-docx file.md`（不写 `convert`）仍然有效。

---

## `convert` — 正向编译（Markdown → DOCX）

### 基本用法

```bash
md-to-docx [选项] PATH
md-to-docx convert [选项] PATH
```

**`PATH`** — 单个 `.md` 文件，或一个目录。目录会递归扫描所有 `*.md`。

### 输入与输出

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `PATH` | 必填 | 要转换的 Markdown 文件或目录 |
| `--output-dir DIR` | 源文件旁边 | 把所有 `.docx` 写到指定目录。扫目录时会保留相对路径（如 `docs/a/x.md` → `DIR/a/x.docx`） |
| `--exclude PATTERN` | 见下文 | 排除匹配 glob 的文件，可多次使用 |
| `--skip-existing` | 关 | 若输出 `.docx` 已存在则跳过 |
| `--dry-run` | 关 | 只打印计划转换的文件，不实际写入 |

**目录扫描默认排除：** `README.md`、`CHANGELOG.md`、`SKILL.md`、`.github/**`。  
**始终跳过的目录：** `.git/`、`node_modules/`。

```bash
md-to-docx ./docs --output-dir ./output --exclude "*.draft.md"
md-to-docx ./docs --dry-run
md-to-docx report.md --skip-existing
```

### 模板

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--preset NAME` | 无 | 一键套用模板 + 默认选项。可选：`professional`、`editorial`、`technical`、`academic`、`business`、`report` |
| `--template PATH` | 内置 reference | 自定义 `.docx` 模板 |

**各 preset 默认行为**（命令行显式指定的参数会覆盖 preset）：

| Preset | 目录 | 章节编号 |
|--------|------|----------|
| `professional` | 有 | 无 |
| `editorial` | 有 | 无 |
| `technical` | 有 | 有 |
| `academic` | 有 | 有 |
| `business` | 无 | 无 |
| `report` | 有 | 无 |

字体与样式细节见 [presets.md](presets.md)。

```bash
md-to-docx report.md --preset technical
md-to-docx report.md --template templates/my-template/template.docx
md-to-docx report.md --template custom.docx
```

### 文档结构

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--toc` | 关（preset 可开启） | 插入 Word 目录 |
| `--no-toc` | — | 即使 preset 开了目录也关闭 |
| `--toc-title TEXT` | `Contents` | 目录标题文字 |
| `--numbering` | 关（preset 可开启） | 章节/标题自动编号 |
| `--no-page-numbers` | 关 | 页脚不显示页码 |

```bash
md-to-docx report.md --preset professional --toc --numbering
md-to-docx report.md --no-toc
```

### 文档元数据

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--title TEXT` | 来自 frontmatter | 文档标题 |
| `--author TEXT` | 来自 frontmatter | 作者 |
| `--date TEXT` | 来自 frontmatter | 日期 |
| `--doc-version TEXT` | 无 | 页眉/页脚中的版本号 |

若未指定参数，也会读取 Markdown 顶部的 YAML frontmatter。

### 题注与交叉引用标签

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--figure-label TEXT` | `Figure` | 图题前缀 |
| `--table-label TEXT` | `Table` | 表题前缀 |
| `--section-label TEXT` | `Section` | 章节交叉引用标签 |

### 预处理与插件

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--normalize` | 开 | 转换前修复表格、列表、标题、代码块等常见问题 |
| `--no-normalize` | — | 不预处理，原样转换 |
| `--plugin PATH` | 无 | 加载 Python 转换插件（可多次指定） |
| `--no-plugins` | 关 | 禁用内置插件（mermaid、math、captions） |

```bash
md-to-docx report.md --plugin examples/plugins/uppercase_headings.py
md-to-docx report.md --no-plugins
```

详见 [plugins.md](plugins.md)。

### Mermaid 图表

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--strict-mermaid` | 关 | 文档含 Mermaid 但未安装 `mmdc` 时直接报错退出 |

未安装 `mmdc` 时，图表会以源码代码块形式出现在 Word 里（除非加了 `--strict-mermaid`）。

### 校验模式（`--check`）

只检查 Markdown，**不生成** `.docx`。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--check` | 关 | 仅校验 |
| `--check-format text\|json` | `text` | 输出格式 |
| `--strict` | 关 | 把 warning 当作 error |

```bash
md-to-docx report.md --check
md-to-docx report.md --check --check-format json
md-to-docx ./docs --check --strict
```

校验规则见 [validation.md](validation.md)。

### 全局参数

| 参数 | 说明 |
|------|------|
| `--version` | 打印版本号并退出 |

---

## `reverse` — 反向转换（DOCX → Markdown）

### 基本用法

```bash
md-to-docx reverse INPUT [-o OUTPUT] [选项]
```

| 参数 / 选项 | 默认值 | 说明 |
|-------------|--------|------|
| `INPUT` | 必填 | 源 `.docx` 文件 |
| `-o`, `--output PATH` | 与 `INPUT` 同目录、同主文件名、`.md` | 输出 `.md` 路径 |
| `--version` | — | 打印版本号并退出 |

```bash
md-to-docx reverse report.docx
md-to-docx reverse report.docx -o report.md
```

支持范围与限制见 [roundtrip.md](roundtrip.md)。

---

## `diff` — 对比两个文档

### 基本用法

```bash
md-to-docx diff A B [选项]
```

| 参数 / 选项 | 默认值 | 说明 |
|-------------|--------|------|
| `A` | 必填 | 第一个文档（`.md` 或 `.docx`） |
| `B` | 必填 | 第二个文档 |
| `--format text\|json\|md` | `text` | 输出格式。`md` 为 changelog 风格摘要 |
| `--version` | — | 打印版本号并退出 |

```bash
md-to-docx diff draft-v1.md draft-v2.md
md-to-docx diff old.docx new.docx --format json
md-to-docx diff a.md b.md --format md
```

---

## `build` — 重建模板（开发者）

重建 `assets/` 下的内置 Word 模板。修改样式脚本或发版前使用。

```bash
md-to-docx build presets      # assets/presets/*.docx + reference-native.docx
md-to-docx build all          # 同 presets
```

需要 `python-docx`（基础依赖已包含）。

等价的 module 调用（CI/Docker 仍可使用）：

```bash
python -m md_to_docx.presets_build
```

---

## 环境变量

| 变量 | 默认值 | 作用 |
|------|--------|------|
| `MD_TO_DOCX_MERMAID_SCALE` | `4` | Mermaid PNG 缩放（越大越清晰、文件越大） |
| `MD_TO_DOCX_MERMAID_WIDTH` | 未设置 | mmdc 输出宽度（像素，如 `1200`） |
| `MD_TO_DOCX_BROWSER` | 自动检测 | mmdc 使用的浏览器路径 |
| `PUPPETEER_EXECUTABLE_PATH` | 自动检测 | 同上（Puppeteer 惯例） |

```bash
MD_TO_DOCX_MERMAID_SCALE=5 md-to-docx report.md
```

更多说明见 [configuration.md](configuration.md)。

---

## 退出码

| 代码 | 含义 |
|------|------|
| `0` | 成功（校验仅有 warning 也算成功） |
| `1` | 转换/校验失败，或批量转换部分失败 |
| `2` | 缺少必填参数或用法错误 |

---

## 常见问题

| 现象 / 报错 | 可能原因 | 解决办法 |
|-------------|----------|----------|
| `path does not exist: …` | 文件名或路径错误 | 检查拼写和扩展名（单文件必须是 `.md`） |
| `not a Markdown file` | 路径不是 `.md` | 只转换 Markdown 文件 |
| `no .md files found` | 目录为空或全被排除 | 用 `--dry-run` 查看；调整 `--exclude` |
| `Template not found` | preset 模板缺失 | 运行 `md-to-docx build presets` |
| Mermaid 显示为代码块 | 未安装 `mmdc` | `npm install -g @mermaid-js/mermaid-cli`，或加 `--strict-mermaid` 强制报错 |
| `No module named md_to_docx` | 未安装也未设 PYTHONPATH | 用 `./bin/convert` 或 `pip install -e .` |

完整安装指南：[installation.md](installation.md)。

---

## 延伸阅读

- [预设模板](presets.md) — 各 preset 的字体与样式
- [文档校验](validation.md) — `--check` 规则代码表
- [往返转换](roundtrip.md) — reverse / diff 支持矩阵
- [插件](plugins.md) — 自定义 `--plugin` 转换
- [MCP 服务](mcp.md) — AI 客户端用的 `md-to-docx mcp`
- [配置](configuration.md) — 环境变量与内置资源
- [GitHub Action](../action/README.md) — CI 自动化
