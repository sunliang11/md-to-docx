(function () {
  const ASSISTANT_SELECTORS = [
    "[data-is-streaming='false'] .font-claude-message",
    ".claude-message",
    "[data-testid='conversation'] [data-is-streaming]",
  ];

  function extractLatestAssistantMarkdown(document) {
    const nodes = document.querySelectorAll(
      ".font-claude-message, [data-testid='user-message'] + div, .prose"
    );
    let el = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      if (nodes[i].textContent.trim().length > 20) {
        el = nodes[i];
        break;
      }
    }
    if (!el) {
      el = MdToDocxExtract.findLatestAssistant(document, ASSISTANT_SELECTORS);
    }
    if (!el) return null;
    return {
      markdown: MdToDocxExtract.elementToMarkdown(el),
      title: document.title || "Claude",
    };
  }

  function setup() {
    const observer = new MutationObserver(() => attachButtons());
    observer.observe(document.body, { childList: true, subtree: true });
    attachButtons();
  }

  function attachButtons() {
    const messages = document.querySelectorAll(".font-claude-message, .prose");
    const last = messages[messages.length - 1];
    if (!last) return;
    const parent = last.parentElement || last;
    MdToDocxExport.injectExportButton(parent, () => {
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
