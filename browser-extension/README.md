# Export AI to Word (md-to-docx)

Chrome extension (Manifest V3) to export AI chats and web pages as professional Word DOCX.

Conversion runs on your **local** md-to-docx Playground — not on a cloud service. When Playground is offline, buttons show **Export MD** and download Markdown instead.

## Features (v0.2)

- **Full conversation export** on supported AI sites (user + assistant turns)
- **Batch export** on ChatGPT / Claude / Doubao: checkbox sidebar threads → one combined file
- **Floating button** (**on by default** as a framed circular launcher; click to open export sheet; drag to move)
- **Webpage export**: selection if present, otherwise `article` / `main` / largest content block, with cleaner Markdown spacing
- Offline-aware labels: **Export to Word** vs **Export MD**

## Where the button appears

### AI chat sites (message toolbar + floating + batch where supported)

| Site | URL pattern | Batch sidebar |
|------|-------------|---------------|
| ChatGPT | `https://chatgpt.com/*` | Yes |
| Claude | `https://claude.ai/*` | Yes |
| Gemini | `https://gemini.google.com/*` | — |
| DeepSeek | `https://chat.deepseek.com/*` | — |
| Kimi | `https://kimi.moonshot.cn/*`, `https://www.kimi.com/*` | — |
| Doubao (豆包) | `https://www.doubao.com/*` | Yes |

### Floating button (any page, including AI sites)

**On by default as a framed circular FAB** — click to open a light export sheet, then export. Drag to move. Click outside, Esc, or × to close the sheet. Uncheck *Show floating export button* in Options to remove it completely.

The extension requests broad host access for webpage export; content still goes only to your configured local endpoint.

### Does NOT work

- Cursor / VS Code **embedded** AI chat panels
- `chrome://` and other non-http(s) pages
- The local Playground page itself is excluded from the generic webpage script

## Setup

### 1. Start the Playground

```bash
docker compose -f web/docker-compose.yml up --build
```

Default endpoint: `http://127.0.0.1:8080`

### 2. Load the extension

1. Open `chrome://extensions`
2. Enable **Developer mode**
3. **Load unpacked** → select the `browser-extension/` folder
4. Accept the expanded host permission (needed for the floating webpage button)

### 3. Options

Click extension → Options (or open `src/options.html`):

- **Endpoint URL** — Playground base URL
- **Preset** — default `technical`
- **Fallback .md** — download markdown if convert fails / offline
- **Show floating button** — framed circular launcher; click to open export sheet

## Usage

1. Start the Playground (optional; offline → MD)
2. Open a supported AI site or any webpage in Chrome
3. **Current chat:** click **Export to Word** / **Export MD** on the last reply → exports the **full** open conversation
4. **Batch:** tick checkboxes in the sidebar (ChatGPT / Claude / Doubao) → **Export selected (N)** → one combined document
5. **Webpage / floating:** click the circular launcher → **Export to Word** / **Export MD** in the sheet (or select text first)

After installing or updating the extension, **refresh** open tabs. Reloading the extension without refreshing leaves a dead content script that cannot call `chrome.storage`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Button says Export MD | Playground not reachable at the endpoint — start Docker or fix Options URL |
| No floating button | Options → enable *Show floating export button*, Save, then refresh. On generic sites (e.g. Zhihu) only the circular **MD** FAB appears — set extension Site access to **On all sites**, refresh the tab. After this version, SPA pages that wipe the DOM remount the FAB automatically. |
| Floating is only a circle | Click the launcher to open the export sheet |
| Doubao: no toolbar button | Enable floating button as fallback; refresh after update |
| Batch missing threads | Scroll the sidebar so items are rendered, then tick them |
| Using Cursor side panel | Switch to a Chrome tab |
| Extension just installed | Refresh the page |
| Extension context invalidated / export fails after reload | Reload the extension, then **refresh open tabs** so content scripts reconnect |

## Privacy

Content is sent only to the endpoint you configure (default `127.0.0.1`). No third-party conversion API.

## Tests

```bash
cd browser-extension
npm install
npm test
```

Uses jsdom + HTML fixtures in `testdata/`. Site DOM changes may break adapters — update selectors in `src/content/`.

## Icons

Regenerate: `python scripts/generate_extension_icons.py`

## Demo narrative

Open Claude → ask for a report → **Export to Word** → open `document.docx` in Word. Or select several sidebar chats → **Export selected**.
