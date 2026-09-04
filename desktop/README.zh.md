# 桌面右键菜单 — Finder / 资源管理器

一键安装 **系统右键** 菜单（仅当前用户，无需管理员）。

| 文件 | 操作 |
|------|------|
| `.md` / `.markdown` | **Convert to Word (md-to-docx)** → `md-to-docx <file> --preset technical` |
| `.docx` | **Reverse to Markdown (md-to-docx)** → `md-to-docx reverse <file>` |

输出写在源文件同目录（与 CLI 一致）。

## 前置条件

1. 先把 CLI 装到 `PATH`（或设置绝对路径环境变量 `MD_TO_DOCX_CLI`）：

```bash
pip install -e .          # 在本仓库根目录
which md-to-docx          # macOS / Linux
where md-to-docx          # Windows
```

2. 在**仓库根目录**执行下方安装脚本。

## 安装

### macOS（Finder 服务）

```bash
bash desktop/macos/install.sh
```

然后在 Finder 中：右键 `.md` 或 `.docx`，在菜单**底部**查找 **Convert to Word (md-to-docx)** / **Reverse to Markdown (md-to-docx)**。服务项较少时直接出现在主菜单；较多时在 **服务** 子菜单里。

若看不到菜单：

1. **系统设置 → 通用 → 登录项与扩展 → 扩展 → Finder**（勾选 md-to-docx 相关项），或
2. **系统设置 → 键盘 → 键盘快捷键 → 服务**，或
3. 重新运行 `install.sh`，或注销后重新登录。

### Windows（资源管理器）

```powershell
powershell -ExecutionPolicy Bypass -File desktop/windows/install.ps1
```

然后在资源管理器中右键 `.md` 或 `.docx`。

## 卸载

```bash
# macOS
bash desktop/macos/uninstall.sh
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File desktop/windows/uninstall.ps1
```

卸载只移除右键挂钩与本地 runner/配置，**不会**卸载 `md-to-docx` Python 包。

## 配置

| 平台 | 配置文件 |
|------|----------|
| macOS | `~/Library/Application Support/md-to-docx/context-menu.conf` |
| Windows | `%LOCALAPPDATA%\md-to-docx\context-menu.conf` |

```bash
CLI="/absolute/path/to/md-to-docx"
PRESET="technical"
EXTRA_ARGS=""
```

- **CLI** — 安装时写入的绝对路径（GUI 启动的菜单通常没有你的 shell `PATH`）
  macOS 安装脚本会通过 **Homebrew 或 root pyenv** 解析到 `~/.pyenv/versions/<ver>/bin/md-to-docx`（不要把 conf 写成 `shims/` 路径，Finder 无法运行 shim）。
- **PRESET** — 正向转换的 `--preset`（默认 `technical`）
- **EXTRA_ARGS** — 可选额外 CLI 参数（空格分隔）
- **`MD_TO_DOCX_CLI`** — 安装或运行时可覆盖配置中的 `CLI`

升级 CLI 后请重新运行安装脚本，以刷新绝对路径。

## 排错

| 现象 | 处理 |
|------|------|
| 菜单不出现（macOS） | 看 Finder 右键菜单**底部** / **服务**；在「通用 → 登录项与扩展 → 扩展 → Finder」或「键盘快捷键 → 服务」中启用；重跑 install / 注销登录 |
| 点了没反应（macOS） | 重跑 `bash desktop/macos/install.sh`；查看 `~/Library/Logs/md-to-docx/context-menu.log` — 点击后若完全没有 `START` 行，说明服务未执行（不是 CLI 失败） |
| 菜单不出现（Windows） | 重新运行 `install.ps1`；检查 HKCU `SystemFileAssociations` |
| 提示 “CLI not found” | 把 `md-to-docx` 加入 PATH，或设置 `MD_TO_DOCX_CLI` 后重装 |
| 终端能转、右键不能 | 需固化绝对路径 — 在 `which`/`where` 可用的 shell 里重跑 install |
| preset 不对 | 直接改配置文件里的 `PRESET=`（不必重装） |

## 目录

```
desktop/
  README.md / README.zh.md
  macos/install.sh  uninstall.sh  lib/runner.sh
  windows/install.ps1  uninstall.ps1  lib/runner.ps1
```
