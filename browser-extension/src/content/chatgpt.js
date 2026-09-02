(function () {
  const ASSISTANT_SELECTORS = [
    "[data-message-author-role='assistant']",
    ".markdown",
  ];

  function extractLatestAssistantMarkdown(document) {
    const el = MdToDocxExtract.findLatestAssistant(document, ASSISTANT_SELECTORS);
    if (!el) return null;
    const markdown = MdToDocxExtract.elementToMarkdown(el);
    const title = document.title || "ChatGPT";
    return { markdown, title };
  }

  function setup() {
    const observer = new MutationObserver(() => attachButtons());
    observer.observe(document.body, { childList: true, subtree: true });
    attachButtons();
  }

  function attachButtons() {
    const messages = document.querySelectorAll("[data-message-author-role='assistant']");
    const last = messages[messages.length - 1];
    if (!last) return;
    const toolbar = last.querySelector(".flex.items-center") || last;
    MdToDocxExport.injectExportButton(toolbar, () => {
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

  if (typeof module !== "undefined" && module.exports) {
    module.exports.extractLatestAssistantMarkdown = extractLatestAssistantMarkdown;
  }
})();
