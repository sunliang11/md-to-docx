(function (global) {
  const DEFAULTS = {
    endpoint: "http://127.0.0.1:8080",
    preset: "technical",
    fallbackMd: true,
  };

  function showToast(message) {
    const existing = document.querySelector(".md-to-docx-toast");
    if (existing) existing.remove();
    const el = document.createElement("div");
    el.className = "md-to-docx-toast";
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 6000);
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  function downloadText(text, filename) {
    downloadBlob(new Blob([text], { type: "text/markdown" }), filename);
  }

  async function getSettings() {
    return new Promise((resolve) => {
      chrome.storage.sync.get(DEFAULTS, (items) => resolve(items));
    });
  }

  async function convertAndDownload(markdown, title) {
    const settings = await getSettings();
    const safeTitle = global.MdToDocxExtract.sanitizeTitle(title);
    const endpoint = settings.endpoint.replace(/\/$/, "");

    try {
      const res = await fetch(endpoint + "/api/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          markdown,
          preset: settings.preset,
          toc: true,
        }),
      });

      if (!res.ok) {
        let detail = "Convert failed";
        try {
          const json = await res.json();
          detail = json.detail?.problem || json.detail?.cause || JSON.stringify(json.detail);
        } catch (_) {
          detail = res.statusText;
        }
        throw new Error(detail);
      }

      const blob = await res.blob();
      downloadBlob(blob, safeTitle + ".docx");
      showToast("Downloaded " + safeTitle + ".docx");
    } catch (err) {
      if (settings.fallbackMd) {
        downloadText(markdown, safeTitle + ".md");
      }
      showToast(
        (err.message || "Export failed") +
          ". Start playground: docker compose -f web/docker-compose.yml up --build"
      );
    }
  }

  function injectExportButton(container, onClick) {
    if (!container || container.querySelector(".md-to-docx-export-btn")) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "md-to-docx-export-btn";
    btn.textContent = "Export to Word";
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      onClick();
    });
    container.appendChild(btn);
  }

  global.MdToDocxExport = {
    convertAndDownload,
    injectExportButton,
    showToast,
  };
})(typeof window !== "undefined" ? window : globalThis);
