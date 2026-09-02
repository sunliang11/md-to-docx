# Export AI to Word (md-to-docx)

Chrome extension (Manifest V3) to export AI chat replies as professional Word DOCX.

Conversion runs on your **local** md-to-docx Playground — not on a cloud service.

## Supported sites

- ChatGPT (`chatgpt.com`)
- Claude (`claude.ai`)
- Gemini (`gemini.google.com`)
- DeepSeek (`chat.deepseek.com`)
- Kimi (`kimi.moonshot.cn`, `www.kimi.com`)
- Doubao (`www.doubao.com`)

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

1. Open an AI chat with a reply visible
2. Click **Export to Word** on the latest assistant message
3. DOCX downloads via local Playground

If the Playground is not running, the extension downloads `.md` and shows a toast with Docker instructions.

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
