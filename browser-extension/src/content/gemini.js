(function () {
  function extractLatestAssistantMarkdown(document) {
    const el = MdToDocxExtract.findLatestAssistant(document, [
      "message-content",
      ".model-response-text",
      ".response-container",
      ".markdown",
    ].map((s) => (s.startsWith(".") ? s : "[class*='" + s + "']")));
    const fallback = document.querySelector(".model-response-text, .response-content, .markdown");
    const node = el || fallback;
    if (!node) return null;
    return {
      markdown: MdToDocxExtract.elementToMarkdown(node),
      title: document.title || "Gemini",
    };
  }

  function setup() {
    const observer = new MutationObserver(() => attachButtons());
    observer.observe(document.body, { childList: true, subtree: true });
    attachButtons();
  }

  function attachButtons() {
    const nodes = document.querySelectorAll(".model-response-text, .response-content, .markdown");
    const last = nodes[nodes.length - 1];
    if (!last) return;
    MdToDocxExport.injectExportButton(last.parentElement || last, () => {
      const data = extractLatestAssistantMarkdown(document);
      if (!data || !data.markdown.trim()) {
        MdToDocxExport.showToast("Could not find an AI reply on this page");
        return;
      }
      MdToDocxExport.convertAndDownload(data.markdown, data.title);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }

  if (typeof module !== "undefined") module.exports = { extractLatestAssistantMarkdown };
})();
