(function () {
  function extractTurns(document) {
    const turns = [];
    const nodes = document.querySelectorAll(
      ".chat-message, .message-item, [class*='message'], .markdown-body, .message-content"
    );
    const seen = new Set();
    nodes.forEach((node) => {
      const content =
        node.querySelector(".markdown-body, .message-content") || node;
      if (seen.has(content)) return;
      const text = (content.textContent || "").trim();
      if (text.length < 2) return;
      seen.add(content);
      const cls = ((node.className && String(node.className)) || "") + " " +
        ((content.className && String(content.className)) || "");
      const isUser = /user|human|question|send/i.test(cls);
      turns.push({ role: isUser ? "user" : "assistant", el: content });
    });
    return turns;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) return null;
    const title = document.title || "Kimi";
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
      title: document.title || "Kimi",
    };
  }

  function attachButtons() {
    const nodes = document.querySelectorAll(".markdown-body, .message-content");
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
