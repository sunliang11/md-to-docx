# P2C — Browser Extension：Export AI to Word（v2.5）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1D `DONE`，P2B `/api/convert` 已存在（扩展把 Markdown POST 到转换服务）
> **Depends on:** P2A（推荐）、P2B（硬：需要 convert HTTP 或把引擎编译进扩展——后者禁止）
> **Target version:** 扩展独立版本 `0.1.0`，引擎不必 bump

---

## Execution contract

### Goal

在 ChatGPT / Claude / Gemini / DeepSeek / Kimi / 豆包 的对话页出现 **Export to Word**。点击后抽取当前 AI 回答的 Markdown，转成 DOCX 下载。

### 禁止

- 「万能网页转 Word」
- 把页面 HTML 当 Word 导出（必须尽量还原 Markdown）
- 扩展内实现 AST/DOCX（WASM 全套太重，且会分叉）
- 强制用户把对话上传到你们云。默认：本机 Playground `http://127.0.0.1:8080` 或「仅下载 .md」降级
- 窃取 cookie、读全部浏览历史、任意站注入

### Done when

- [ ] Chrome Manifest V3 扩展在 `browser-extension/`
- [ ] 上述站点白名单 content script
- [ ] 按钮 Export to Word
- [ ] 选项页：convert endpoint、preset
- [ ] 端点不可达时：下载 `.md` 并提示跑 Docker Playground 或 CLI
- [ ] README 演示 GIF 叙事：打开 Claude → Export → 得到 Word

---

## 锁定决策

1. **转换发生在本地 HTTP 引擎（P2B）或用户配置的自托管 URL。** 扩展只做抽取 + POST + 下载。
2. **抽取策略按站点适配器。** 每个适配器返回 `{markdown: string, title: string}`。不要一个巨大 regex。
3. **权限：** `activeTab` + host_permissions 仅白名单 + `storage`。不要 `https://*/*`。
4. **Firefox** 本阶段不做，但避免明显不兼容 MV3 API，方便以后。
5. **仍不拆 git 仓库**，目录 `browser-extension/`。
6. **不发 Chrome Web Store** 除非用户要求。文档写 Load unpacked。

---

## 目录结构

```
browser-extension/
  README.md
  manifest.json
  src/background.js
  src/options.html
  src/options.js
  src/content/chatgpt.js
  src/content/claude.js
  src/content/gemini.js
  src/content/deepseek.js
  src/content/kimi.js
  src/content/doubao.js
  src/button.css
  src/lib/extract.js
  src/lib/export.js
  icons/icon16.png
  icons/icon48.png
  icons/icon128.png     # 从 assets/branding/logo.svg 导出 PNG
```

---

## Task 1 — manifest 与按钮注入

`manifest.json` MV3：

- `content_scripts` matches 锁定（实现时再核对真实域名，写进 Execution log）：
  - `https://chatgpt.com/*`
  - `https://claude.ai/*`
  - `https://gemini.google.com/*`
  - `https://chat.deepseek.com/*`
  - `https://kimi.moonshot.cn/*` 与 `https://www.kimi.com/*`（以当时为准）
  - `https://www.doubao.com/*` / `https://www.volcengine.com/*` 豆包实际对话域
- 每个文件独立 matches，避免在错误站跑错误适配器

按钮：固定在**最后一条 assistant 消息**工具条旁，文案 `Export to Word`，不要遮挡输入框。

---

## Task 2 — 适配器

每个适配器：

```js
export function extractLatestAssistantMarkdown(document) {
  return { markdown, title }
}
```

优先：站点若有「复制 Markdown」按钮，用其数据源（DOM 属性/data）。否则：从消息节点做 HTML→Markdown（白名单标签：p, h1-h6, pre/code, ul/ol/li, table, a, img, blockquote, em, strong）。用现成小函数，不要引入巨大 turndown 除非体积可接受。允许依赖 `turndown` 打进扩展（单文件 vendor）。

代码块：保留 fence 语言 class。

失败：toast `Could not find an AI reply on this page`。

每个适配器 `tests` 用 jsdom 夹具 HTML（保存匿名化 DOM 快照在 `browser-extension/testdata/`）。站点改版会挂，测试至少保证选择器模块化。

---

## Task 3 — Export 流程

1. extract
2. `chrome.storage` 读 `endpoint`（默认 `http://127.0.0.1:8080`）和 `preset`（默认 `technical`）
3. `POST ${endpoint}/api/convert` JSON
4. 成功：`download` API 存 `title.docx`
5. 失败：保存 `title.md`，badge 提示 `Start playground: docker compose ...`

CORS：P2B FastAPI 必须允许扩展 origin。给 P2B 补：`chrome-extension://*` CORS。若 P2B 已 `*`，足够。

本地 HTTP：扩展访问 `127.0.0.1` 在 Chrome 可能要提示用户。选项页写明。

---

## Task 4 — 选项页

字段：Endpoint URL、Preset select、Fallback download markdown checkbox（默认 true）。

保存 chrome.storage.sync。

---

## Task 5 — 图标与文档

从 P0 SVG 导出 PNG。`browser-extension/README.md`：Load unpacked 步骤、隐私（对话只发到你填的 endpoint）、站点列表。

根 README Integration 列表加 Browser extension。

不要在 SKILL.md 写扩展（那是 agent 路径）。

---

## 验收

- `python -m json.tool browser-extension/manifest.json`
- jsdom 单测若用 Node：`browser-extension/package.json` 仅 devDependencies，不要让根 Python CI 必须跑 npm。扩展测试：`npm test` 写在 extension README，根 CI **可选** job `extension`（可先 skip）。
- 人工：Docker playground 开着，chatgpt.com 或任意一个适配器页（无账号则用 testdata + mock）

Agent 无真实 ChatGPT 登录时：用 testdata HTML 跑抽取单测即视为代码完成，Execution log 标明未实站点击。

---

## Handoff

P3 不要把扩展改成 IDE。VS Code 是另一条入口。

---

## Execution log

**2026-09-02** — P2C complete.

Domains in manifest: `chatgpt.com`, `claude.ai`, `gemini.google.com`, `chat.deepseek.com`, `kimi.moonshot.cn`, `www.kimi.com`, `www.doubao.com`.

```bash
python -m json.tool browser-extension/manifest.json
cd browser-extension && npm test   # 4 passed
```

No live site click (no logged-in session); testdata HTML + jsdom adapters verified. CI job `extension` added.
