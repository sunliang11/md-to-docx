(function (global) {
  const CHECKBOX_CLASS = "md-to-docx-batch-cb";
  const BAR_CLASS = "md-to-docx-batch-bar";
  const SELECTED = new Map(); // id -> { id, title, el }

  function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function waitFor(predicate, timeoutMs, intervalMs) {
    const timeout = timeoutMs || 8000;
    const interval = intervalMs || 200;
    const start = Date.now();
    return new Promise((resolve) => {
      const tick = () => {
        try {
          if (predicate()) {
            resolve(true);
            return;
          }
        } catch (_) {}
        if (Date.now() - start >= timeout) {
          resolve(false);
          return;
        }
        setTimeout(tick, interval);
      };
      tick();
    });
  }

  function updateBar(bar) {
    if (!bar) return;
    const n = SELECTED.size;
    const btn = bar.querySelector(".md-to-docx-batch-export");
    const label = bar.querySelector(".md-to-docx-batch-count");
    if (label) label.textContent = String(n);
    if (btn) {
      btn.disabled = n === 0;
      btn.textContent = "Export selected (" + n + ")";
    }
  }

  function ensureBar(onExport) {
    let bar = document.querySelector("." + BAR_CLASS);
    if (bar) return bar;
    bar = document.createElement("div");
    bar.className = BAR_CLASS;
    bar.innerHTML =
      '<span class="md-to-docx-batch-label">md-to-docx: <strong class="md-to-docx-batch-count">0</strong> selected</span>' +
      '<button type="button" class="md-to-docx-export-btn md-to-docx-batch-export" disabled>Export selected (0)</button>';
    const btn = bar.querySelector(".md-to-docx-batch-export");
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      onExport();
    });
    document.body.appendChild(bar);
    return bar;
  }

  function attachCheckbox(item, bar) {
    if (!item || !item.el || item.el.querySelector("." + CHECKBOX_CLASS)) return;
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.className = CHECKBOX_CLASS;
    cb.title = "Select for batch export";
    cb.addEventListener("click", (e) => e.stopPropagation());
    cb.addEventListener("change", (e) => {
      e.stopPropagation();
      if (cb.checked) {
        SELECTED.set(item.id, item);
      } else {
        SELECTED.delete(item.id);
      }
      updateBar(bar);
    });
    if (SELECTED.has(item.id)) cb.checked = true;

    const host = item.el;
    if (getComputedStyle(host).position === "static") {
      host.style.position = "relative";
    }
    host.insertBefore(cb, host.firstChild);
  }

  /**
   * @param {{
   *   listSidebarConversations: () => {id:string,title:string,el:Element}[],
   *   openConversation: (item) => Promise<void>,
   *   extractConversationMarkdown: (document) => {markdown:string,title:string}|null,
   *   isConversationReady?: () => boolean,
   * }} hooks
   */
  function setupBatchExport(hooks) {
    if (!hooks || typeof hooks.listSidebarConversations !== "function") return;

    const bar = ensureBar(async () => {
      const items = Array.from(SELECTED.values());
      if (!items.length) return;
      const sections = [];
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        global.MdToDocxExport.showToast(
          "Exporting " + (i + 1) + "/" + items.length + ": " + (item.title || item.id)
        );
        try {
          await hooks.openConversation(item);
          const ready =
            typeof hooks.isConversationReady === "function"
              ? await waitFor(() => hooks.isConversationReady(), 10000)
              : await wait(900);
          if (!ready && typeof hooks.isConversationReady === "function") {
            await wait(500);
          }
          const data = hooks.extractConversationMarkdown(document);
          const title = (data && data.title) || item.title || item.id;
          const body = (data && data.markdown) || "";
          if (body.trim()) {
            sections.push("## Session: " + title + "\n\n" + body.trim());
          }
        } catch (err) {
          global.MdToDocxExport.showToast(
            "Failed: " + (item.title || item.id) + " — " + (err.message || err)
          );
        }
      }

      if (!sections.length) {
        global.MdToDocxExport.showToast("No conversation content found for selection");
        return;
      }

      const markdown = "# Batch export\n\n" + sections.join("\n\n---\n\n");
      const title = "batch_export_" + items.length + "_sessions";
      await global.MdToDocxExport.convertAndDownload(markdown, title);
    });

    function sync() {
      const list = hooks.listSidebarConversations() || [];
      for (const item of list) {
        attachCheckbox(item, bar);
      }
      updateBar(bar);
    }

    const observer = new MutationObserver(() => sync());
    observer.observe(document.body, { childList: true, subtree: true });
    sync();
    return { sync, bar };
  }

  global.MdToDocxBatch = {
    setupBatchExport,
    wait,
    waitFor,
  };
})(typeof window !== "undefined" ? window : globalThis);
