# Export AI to Word (md-to-docx)

Chrome extension (Manifest V3) to export AI chat replies as professional Word DOCX.

Conversion runs on your **local** md-to-docx Playground — not on a cloud service.

## Where the button appears

**Important:** The **Export to Word** button is injected only on real AI chat websites opened in **Chrome** (or another Chromium browser). Starting the Playground does **not** add a button to the Playground page itself.

### Works — extension injects on these URLs only

Primary sites:

- **`https://chatgpt.com/*`**
- **`https://claude.ai/*`**
- **`https://gemini.google.com/*`**

Full list (matches `manifest.json`):

| Site | URL pattern |
|------|-------------|
| DeepSeek | `https://chat.deepseek.com/*` |
| ChatGPT | `https://chatgpt.com/*` |
| Claude | `https://claude.ai/*` |
| Gemini | `https://gemini.google.com/*` |

The Playground and the AI site do **not** need to be in the same window — keep Playground running in the background on port 8080.

### Does NOT work — no button will appear

- Cursor / VS Code **embedded** AI chat panels or built-in browser
- The local Playground page (`http://127.0.0.1:8080`) — that page is the *converter*, not an AI chat site
- `chat.openai.com` (legacy URL; use `chatgpt.com`)
- Any page whose URL is not in the table above

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

### 3. Options

Click extension → Options (or open `src/options.html`):

- **Endpoint URL** — Playground base URL
- **Preset** — default `technical`
- **Fallback .md** — download markdown if convert fails

## Usage

1. Start the Playground and keep it running on port 8080
2. Open **Chrome** (or Edge) in a **new tab** → go to `https://chatgpt.com` (or Claude, Gemini, etc.)
3. Log in, start a chat, and wait for an **assistant reply**
4. Click the blue **Export to Word** button on the **latest assistant message**
5. Your browser downloads a `.docx` file

After installing or updating the extension, **refresh** any AI chat tabs that were already open.

If the Playground is not running, the extension downloads `.md` and shows a toast with Docker instructions.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Using Cursor side panel | Switch to a Chrome tab on a supported URL (see table above) |
| Playground open but no button | Playground does not show the button — open an AI chat site |
| Extension just installed | Refresh the AI chat page |
| Wrong URL | Must be `chatgpt.com`, not an embedded or legacy view |
| No assistant reply yet | Send a message and wait for the AI response |
| Site DOM changed | Try another supported site; update selectors in `src/content/` |

## Alternatives (Cursor / no extension)

If you are chatting inside Cursor or another unsupported panel:

- **Playground** — copy Markdown → paste into `http://127.0.0.1:8080` → **Generate DOCX**
- **CLI** — `./bin/convert report.md --preset technical`
- **Re-open in Chrome** — paste the content into `chatgpt.com` (or another supported site) and use **Export to Word**

## Privacy

Chat content is sent only to the endpoint you configure (default `127.0.0.1`). No third-party conversion API.

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

Open Claude → ask for a report → **Export to Word** → open `document.docx` in Word.
