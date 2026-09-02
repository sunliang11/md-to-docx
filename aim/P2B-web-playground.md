# P2B — Web Playground + Docker（v1.5 / v2.0 体验层）

> **For AI agents:** Read this entire file before writing any code.
> **Prerequisite:** P1D `DONE`。P2A 的 `api.convert` 若已存在必须复用；若 P2A 未做，本 plan 允许直接调 `api.py`——若 `api.py` 还不存在，先把 P2A Task 1 做完再继续，不要复制引擎。
> **Depends on:** P1D（硬）、P2A Task 1（软）
> **Unblocks:** P2C
> **Target version:** 体验层，不强制 bump 引擎大版本。Playground 作为仓库子目录 `web/`。

---

## Execution contract

### Goal

陌生人 30 秒、无需本地安装，把一段 AI Markdown 变成可下载的 DOCX。这是 Demo 驱动增长的落地页。

### 禁止

- 账号系统、计费、多租户、把用户文档存对象存储当产品（可 ephemeral /tmp）
- 调用 OpenAI API「帮你改文章」
- 在浏览器用 JS 重写一份 Markdown→DOCX
- 一开始就做 Cloud API 网关（P4）
- 把 playground 做成必须连官方 SaaS 才能用 CLI

### Done when

- [ ] `web/` 能本地 `docker compose up` 打开编辑器 + Generate DOCX
- [ ] 左侧 Markdown，右侧 **HTML 近似预览**（不是真 Word 排版引擎，UI 要标明 Preview approximation）
- [ ] 可选手 preset，下载 docx
- [ ] 无安装路径：README 有「Try locally with Docker」；若无公开托管，不要在 GitHub README 放死链 Try Online
- [ ] 转换走 Python 引擎，同一套 presets
- [ ] 有基础限流：body 大小上限、超时

---

## 锁定决策

1. **技术栈：**
   - 后端：FastAPI，调用 `md_to_docx.api.convert`
   - 前端：单页，无 React 强迫。锁定 **Vite + vanilla TS** 或 **单 HTML +  codemirror 6 CDN**。为减少依赖：**FastAPI 托管 `web/static`，前端一个 `index.html` + `app.js` + `app.css` + textarea**。Preview 用 `markdown-it` 在浏览器渲染 HTML。够 30 秒体验。
   - 不要 Next.js、不要 SSR。
2. **布局（ASCII 已在 aim.md）：** 左右分栏 50/50，顶栏：preset `<select>`、按钮 `Generate DOCX`、`Copy CLI command`。
3. **托管：** P2B 默认只交付 Docker 自托管。GitHub README 的 Try Online 仅当用户稍后自己部署（Pages 不能跑 Python）。可加 `Dockerfile` 注释 fly.io/render 一键，但 **不要** 注册云账号。
4. **隐私文案：** 页脚 `Documents are converted in memory/temp and deleted. Self-host with Docker.`
5. **体积上限：** Markdown 400KB，上传图片每张 5MB，最多 20 张。超时 30s。
6. **Mermaid：** Playground 调后端 native 引擎；容器内可选安装 mermaid-cli（Docker image 分 `slim` 无 mmdc / `full` 有）。默认 compose 用 `slim`，README 说明 flowchart 在 slim 里当代码块。
7. **仍不拆仓库。** `web/` 留在 md-to-docx 内。

---

## 目录结构

```
web/
  README.md
  Dockerfile
  Dockerfile.full          # optional mermaid
  docker-compose.yml
  app.py                   # FastAPI
  static/index.html
  static/app.js
  static/app.css
  examples/                # 启动时加载的示例 md（可 symlink ../../examples）
tests/test_web_api.py      # 只测 FastAPI，用 TestClient
```

根 README 链 `web/README.md`。`.dockerignore` 排除 `.git` tests fixtures 大文件。

---

## Task 1 — FastAPI

```python
POST /api/convert
Content-Type: application/json
{ "markdown": "...", "preset": "technical", "toc": true }

→ application/vnd.openxmlformats-officedocument.wordprocessingml.document
  Content-Disposition: attachment; filename="document.docx"
```

`GET /api/presets` → 列表。

`GET /healthz` → `{"ok": true, "version": "..."}`

错误 JSON：`{"problem","cause","fix"}`，HTTP 400/413/500。

不要 GET convert（URL 太长）。

CORS：默认只 `*` 给自托管；注释生产应变。

---

## Task 2 — 静态前端

- textarea 等宽字体，placeholder 为 `# Technical Report`
- 右侧 preview 随输入 debounce 300ms 刷新（纯前端 markdown-it，**不**调后端）
- Generate：fetch `/api/convert`，blob download `document.docx`
- 失败：alert 区域显示 problem/cause/fix
- 示例下拉：加载 `/examples/technical-report.md` 等 FastAPI 从仓库 examples 读
- 无登录、无 localStorage 强制；可用 localStorage 存最后草稿（可选加分）

无障碍：按钮可键盘点；对比度不要灰字灰底。

---

## Task 3 — Docker

`web/Dockerfile`：

- `python:3.12-slim-bookworm`
- 安装项目 `pip install /app`（copy 仓库）
- 系统 **不** 装 pandoc（native 足够）。wecom preset 在 playground 下拉里 **隐藏或标注 needs pandoc**。Playground 只暴露 native presets。
- `CMD uvicorn md_to_docx.web:app` 或 `web.app:app`
- 端口 8080
- 非 root 用户

`docker-compose.yml`：

```yaml
services:
  playground:
    build:
      context: ..
      dockerfile: web/Dockerfile
    ports: ["8080:8080"]
```

`web/README.md`：

```bash
docker compose -f web/docker-compose.yml up --build
# open http://localhost:8080
```

---

## Task 4 — 安全与滥用

- 请求体大小 Starlette `max_part_size`
- convert 在 threadpool，timeout 30s
- 临时文件 `tempfile.TemporaryDirectory` 请求结束删除
- 无路径穿越：只接受 JSON markdown 字符串，不接受服务器本地 path（与 MCP 不同）。**Playground 禁止 `input_path` 读容器文件系统。**
- 不执行 Markdown 里的 HTML script 在 preview：markdown-it html:false

测试：超大 body 413；xss 字符串 preview 转义。

---

## Task 5 — 文档与 Demo 回写

P0 的 hero 若仍是 CLI-only，追加 `assets/demo/playground.png` 占位或 GIF（可选）。README 增加 Docker 一节。**没有公网 URL 就不要写 Try Online 按钮。**

CHANGELOG。

---

## 验收命令

```bash
pip install -e ".[dev]"
pip install fastapi uvicorn httpx
pytest tests/test_web_api.py -v
# 可选
docker compose -f web/docker-compose.yml up --build
curl -sS http://localhost:8080/healthz
```

无 Docker 时：`uvicorn` 本地起，用 TestClient 仍必须全绿。在 Execution log 注明是否做了浏览器手点。

浏览器手点清单（有 browser 工具就做）：

1. 打开首页左右栏可见
2. 选 technical，Generate，下载非空 docx
3. 空 markdown Generate 显示校验错误
4. 预览随输入更新

---

## Handoff

P2C 扩展的「Export」可以 POST 到用户自托管的同一 `/api/convert`，默认 `http://localhost:8080`。不要把扩展绑死官方云。

---

## Execution log

**2026-09-02** — P2B complete.

```bash
pip install -e ".[web,dev]"
pytest tests/test_web_api.py -v   # 6 passed
# Docker: docker compose -f web/docker-compose.yml up --build
```

Delivered: `web/app.py`, static SPA, Dockerfile + compose, `.dockerignore`, `web/README.md`. Browser hand-test not run in CI; TestClient covers API.
