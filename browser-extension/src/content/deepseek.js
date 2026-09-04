(function () {
  function extractTurns(document) {
    const turns = [];
    const nodes = document.querySelectorAll(
      ".ds-message, [class*='message'], .ds-markdown, .markdown-body"
    );
    nodes.forEach((node) => {
      const cls = (node.className && String(node.className)) || "";
      const isUser = /user|human|request/i.test(cls);
      const content =
        node.querySelector(".ds-markdown, .markdown-body") || node;
      if (!(content.textContent || "").trim()) return;
      // Skip pure containers that only wrap another matched node.
      if (
        content !== node &&
        node.matches(".ds-message, [class*='message']") === false &&
        node.querySelector(".ds-markdown")
      ) {
        return;
      }
      turns.push({
        role: isUser ? "user" : "assistant",
        el: content,
      });
    });

    // Deduplicate nested markdown nodes.
    const filtered = [];
    const seen = new Set();
    for (const t of turns) {
      if (seen.has(t.el)) continue;
      seen.add(t.el);
      filtered.push(t);
    }
    return filtered;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) return null;
    const title = document.title || "DeepSeek";
    return {
      markdown: MdToDocxExtract.turnsToMarkdown(turns, title),
      title,
    };
  }

  function extractLatestAssistantMarkdown(document) {
    const turns = extractTurns(document).filter((t) => t.role === "assistant");
    const last = turns[turns.length - 1];
    if (!last) return null;
    return {
      markdown: MdToDocxExtract.elementToMarkdown(last.el),
      title: document.title || "DeepSeek",
    };
  }

  function attachButtons() {
    const nodes = document.querySelectorAll(".ds-markdown, .markdown-body");
    const last = nodes[nodes.length - 1];
    if (!last) return;
    MdToDocxExport.injectExportButton(last.parentElement || last, () => {
      const data = extractConversationMarkdown(document);
      if (!data || !data.markdown.trim()) {
        MdToDocxExport.showToast("Could not find conversation content on this page");
        return;
      }
      MdToDocxExport.convertAndDownload(data.markdown, data.title);
    });
  }

  function setup() {
    const observer = new MutationObserver(() => attachButtons());
    observer.observe(document.body, { childList: true, subtree: true });
    attachButtons();
    MdToDocxExport.injectFloatingButton(() => {
      const data = extractConversationMarkdown(document);
      if (!data || !data.markdown.trim()) {
        MdToDocxExport.showToast("Could not find conversation content on this page");
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
    module.exports = {
      extractLatestAssistantMarkdown,
      extractConversationMarkdown,
    };
  }
})();
