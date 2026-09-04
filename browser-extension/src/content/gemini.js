(function () {
  function extractTurns(document) {
    const turns = [];
    const userBlocks = document.querySelectorAll(
      "user-query, .user-query, [data-message-author-role='user'], .query-text"
    );
    const assistantBlocks = document.querySelectorAll(
      "model-response, .model-response-text, .response-content, .markdown, message-content"
    );

    userBlocks.forEach((el) => {
      if ((el.textContent || "").trim()) turns.push({ role: "user", el });
    });
    assistantBlocks.forEach((el) => {
      if ((el.textContent || "").trim().length > 5) {
        turns.push({ role: "assistant", el });
      }
    });

    if (!turns.length) {
      const nodes = document.querySelectorAll(
        ".model-response-text, .response-content, .markdown"
      );
      nodes.forEach((el) => turns.push({ role: "assistant", el }));
    }
    return turns;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) return null;
    const title = document.title || "Gemini";
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
      title: document.title || "Gemini",
    };
  }

  function attachButtons() {
    const nodes = document.querySelectorAll(
      ".model-response-text, .response-content, .markdown"
    );
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
