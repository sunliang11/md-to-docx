(function () {
  function extractLatestAssistantMarkdown(document) {
    const el = MdToDocxExtract.findLatestAssistant(document, [
      ".markdown-body",
      ".message-content",
      "[class*='assistant']",
    ]);
    if (!el) return null;
    return {
      markdown: MdToDocxExtract.elementToMarkdown(el),
      title: document.title || "Kimi",
    };
  }

  function setup() {
    const observer = new MutationObserver(() => attachButtons());
    observer.observe(document.body, { childList: true, subtree: true });
    attachButtons();
  }

  function attachButtons() {
    const nodes = document.querySelectorAll(".markdown-body, .message-content");
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
