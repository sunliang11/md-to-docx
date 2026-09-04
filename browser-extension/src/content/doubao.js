(function () {
  const ASSISTANT_SELS = [
    ".flow-markdown-body",
    "[data-testid='message_text_content']",
    "[class*='receive'] [class*='markdown']",
    ".markdown-body",
  ];

  function isUserBubble(el) {
    if (!el) return false;
    const root =
      el.closest(
        "[class*='inner-item-'], [class*='top-item-'], [class*='message'], [data-testid]"
      ) || el.parentElement;
    if (!root) return false;
    const cls = (root.className && String(root.className)) || "";
    if (/send|user|human/i.test(cls)) return true;
    if (root.querySelector("[class*='send-msg'], [class*='user']")) return true;
    // Heuristic: assistant replies contain markdown body; user often plain text without it.
    if (el.matches(".flow-markdown-body") || el.querySelector(".flow-markdown-body")) {
      return false;
    }
    return !el.matches(ASSISTANT_SELS.join(","));
  }

  function messageRoots(document) {
    const roots = document.querySelectorAll(
      "[class*='inner-item-'], [class*='top-item-'], [data-testid='message_text_content']"
    );
    if (roots.length) return Array.from(roots);
    return Array.from(
      document.querySelectorAll(
        ".flow-markdown-body, [data-testid='message_text_content'], .markdown-body"
      )
    );
  }

  function extractTurns(document) {
    const turns = [];
    const roots = messageRoots(document);
    const seen = new Set();

    roots.forEach((root) => {
      const content =
        root.matches("[data-testid='message_text_content'], .flow-markdown-body, .markdown-body")
          ? root
          : root.querySelector(
              ".flow-markdown-body, [data-testid='message_text_content'], .markdown-body"
            ) || root;
      if (!content || seen.has(content)) return;
      const text = (content.textContent || "").trim();
      if (text.length < 2) return;
      seen.add(content);
      const role = isUserBubble(content) ? "user" : "assistant";
      // Prefer markdown body for assistant when nested.
      const el =
        role === "assistant"
          ? content.querySelector(".flow-markdown-body") || content
          : content;
      turns.push({ role, el });
    });

    // If everything was classified assistant but we have user-looking nodes, keep as-is.
    if (!turns.length) {
      const assistants = document.querySelectorAll(ASSISTANT_SELS.join(", "));
      assistants.forEach((el) => {
        if ((el.textContent || "").trim().length > 2) {
          turns.push({ role: "assistant", el });
        }
      });
    }
    return turns;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) return null;
    const title = document.title || "Doubao";
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
      title: document.title || "Doubao",
    };
  }

  function listSidebarConversations() {
    const items = [];
    const seen = new Set();
    const candidates = document.querySelectorAll(
      "#flow_chat_sidebar a[href*='/chat'], [data-testid='chat_list_thread_item'], a[href*='/chat/']"
    );
    candidates.forEach((node, idx) => {
      const anchor = node.tagName === "A" ? node : node.querySelector("a") || node;
      const href = (anchor.getAttribute && anchor.getAttribute("href")) || "";
      const id = href || node.getAttribute("data-testid") || "doubao-" + idx;
      if (seen.has(id)) return;
      seen.add(id);
      const title = (node.textContent || "").replace(/\s+/g, " ").trim() || id;
      items.push({ id, title, el: node, anchor });
    });
    return items;
  }

  function openConversation(item) {
    return new Promise((resolve) => {
      const target = item.anchor || item.el;
      if (target && typeof target.click === "function") target.click();
      setTimeout(resolve, 500);
    });
  }

  function isConversationReady() {
    return (
      document.querySelectorAll(
        ".flow-markdown-body, [data-testid='message_text_content'], [class*='inner-item-']"
      ).length > 0
    );
  }

  function findAttachTarget() {
    const assistants = document.querySelectorAll(
      ".flow-markdown-body, [data-testid='message_text_content']"
    );
    const last = assistants[assistants.length - 1];
    if (!last) return null;
    const item =
      last.closest("[class*='inner-item-'], [class*='top-item-'], [class*='message']") ||
      last.parentElement ||
      last;
    const toolbar =
      item.querySelector("[class*='toolbar'], [class*='action'], [class*='footer']") ||
      item;
    return toolbar;
  }

  function attachButtons() {
    const target = findAttachTarget();
    if (!target) return;
    MdToDocxExport.injectExportButton(target, () => {
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
    // Floating fallback when message toolbar selectors miss.
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
