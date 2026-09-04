(function () {
  function extractTurns(document) {
    const nodes = document.querySelectorAll("[data-message-author-role]");
    const turns = [];
    nodes.forEach((node) => {
      const role = node.getAttribute("data-message-author-role") || "assistant";
      const content =
        node.querySelector(".markdown, .whitespace-pre-wrap") || node;
      turns.push({ role, el: content });
    });
    return turns;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) return null;
    const title = document.title || "ChatGPT";
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
      title: document.title || "ChatGPT",
    };
  }

  function listSidebarConversations() {
    const links = document.querySelectorAll(
      "nav a[href*='/c/'], nav a[href*='/chat/'], a[data-testid^='history-item']"
    );
    const seen = new Set();
    const items = [];
    links.forEach((a, idx) => {
      const href = a.getAttribute("href") || "";
      const id = href || "chatgpt-" + idx;
      if (seen.has(id)) return;
      seen.add(id);
      const title = (a.textContent || "").replace(/\s+/g, " ").trim() || id;
      const el = a.closest("div") || a;
      items.push({ id, title, el, anchor: a });
    });
    return items;
  }

  function openConversation(item) {
    return new Promise((resolve) => {
      const target = item.anchor || item.el.querySelector("a") || item.el;
      if (target && typeof target.click === "function") target.click();
      else if (item.anchor && item.anchor.href) {
        window.location.href = item.anchor.href;
      }
      setTimeout(resolve, 400);
    });
  }

  function isConversationReady() {
    return document.querySelectorAll("[data-message-author-role]").length > 0;
  }

  function attachButtons() {
    const messages = document.querySelectorAll(
      "[data-message-author-role='assistant']"
    );
    const last = messages[messages.length - 1];
    if (!last) return;
    const toolbar = last.querySelector(".flex.items-center") || last;
    MdToDocxExport.injectExportButton(toolbar, () => {
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
    if (globalThis.MdToDocxBatch) {
      MdToDocxBatch.setupBatchExport({
        listSidebarConversations,
        openConversation,
        extractConversationMarkdown,
        isConversationReady,
      });
    }
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
      listSidebarConversations,
    };
  }
})();
