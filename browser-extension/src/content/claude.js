(function () {
  function extractTurns(document) {
    const turns = [];
    const userNodes = document.querySelectorAll(
      "[data-testid='user-message'], .font-user-message"
    );
    const assistantNodes = document.querySelectorAll(
      ".font-claude-message, [data-is-streaming] .prose, .prose"
    );

    // Prefer interleaved walk via common parent when possible.
    const containers = document.querySelectorAll(
      "[data-testid='conversation'] > div, [data-test-render-count], .group\\/message"
    );
    if (containers.length) {
      containers.forEach((node) => {
        if (node.querySelector("[data-testid='user-message'], .font-user-message")) {
          const el =
            node.querySelector("[data-testid='user-message'], .font-user-message") ||
            node;
          turns.push({ role: "user", el });
        } else if (
          node.querySelector(".font-claude-message, .prose") ||
          node.classList.contains("font-claude-message")
        ) {
          const el =
            node.querySelector(".font-claude-message, .prose") || node;
          if ((el.textContent || "").trim().length > 5) {
            turns.push({ role: "assistant", el });
          }
        }
      });
    }

    if (!turns.length) {
      userNodes.forEach((el) => turns.push({ role: "user", el }));
      assistantNodes.forEach((el) => {
        if ((el.textContent || "").trim().length > 5) {
          turns.push({ role: "assistant", el });
        }
      });
    }

    return turns;
  }

  function extractConversationMarkdown(document) {
    const turns = extractTurns(document);
    if (!turns.length) {
      // Fallback: single latest assistant blob
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
      if (!el) return null;
      const title = document.title || "Claude";
      return {
        markdown: MdToDocxExtract.turnsToMarkdown(
          [{ role: "assistant", el }],
          title
        ),
        title,
      };
    }
    const title = document.title || "Claude";
    return {
      markdown: MdToDocxExtract.turnsToMarkdown(turns, title),
      title,
    };
  }

  function extractLatestAssistantMarkdown(document) {
    const data = extractConversationMarkdown(document);
    if (!data) return null;
    const turns = extractTurns(document).filter((t) => t.role === "assistant");
    const last = turns[turns.length - 1];
    if (last) {
      return {
        markdown: MdToDocxExtract.elementToMarkdown(last.el),
        title: data.title,
      };
    }
    return data;
  }

  function listSidebarConversations() {
    const links = document.querySelectorAll(
      "a[href*='/chat/'], nav a[href^='/chat'], [data-testid='chat-row'] a, aside a[href*='/chat']"
    );
    const seen = new Set();
    const items = [];
    links.forEach((a, idx) => {
      const href = a.getAttribute("href") || "";
      const id = href || "claude-" + idx;
      if (seen.has(id)) return;
      seen.add(id);
      const title = (a.textContent || "").replace(/\s+/g, " ").trim() || id;
      const el = a.closest("[data-testid='chat-row']") || a.closest("div") || a;
      items.push({ id, title, el, anchor: a });
    });
    return items;
  }

  function openConversation(item) {
    return new Promise((resolve) => {
      const target = item.anchor || item.el.querySelector("a") || item.el;
      if (target && typeof target.click === "function") target.click();
      setTimeout(resolve, 400);
    });
  }

  function isConversationReady() {
    return (
      document.querySelectorAll(
        ".font-claude-message, [data-testid='user-message'], .prose"
      ).length > 0
    );
  }

  function attachButtons() {
    const messages = document.querySelectorAll(".font-claude-message, .prose");
    const last = messages[messages.length - 1];
    if (!last) return;
    const parent = last.parentElement || last;
    MdToDocxExport.injectExportButton(parent, () => {
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
