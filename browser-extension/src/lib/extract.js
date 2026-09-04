(function (global) {
  function sanitizeTitle(title) {
    return (
      (title || "document")
        .replace(/[<>:"/\\|?*]/g, "")
        .replace(/\s+/g, "_")
        .slice(0, 80) || "document"
    );
  }

  function elementToMarkdown(el) {
    if (!el) return "";
    return global.MdToDocxHtml.htmlToMarkdown(el.innerHTML);
  }

  function findLatestAssistant(_unused, selectors) {
    for (const sel of selectors) {
      const list = document.querySelectorAll(sel);
      if (list.length) return list[list.length - 1];
    }
    return null;
  }

  /**
   * @param {{ role: string, markdown?: string, html?: string, el?: Element }[]} turns
   * @param {string} title
   */
  function turnsToMarkdown(turns, title) {
    const parts = [];
    if (title) parts.push("# " + title.trim(), "");
    for (const turn of turns || []) {
      if (!turn) continue;
      const role = (turn.role || "assistant").toLowerCase();
      const heading = role === "user" ? "### User" : "### Assistant";
      let body = "";
      if (turn.markdown != null && String(turn.markdown).trim()) {
        body = String(turn.markdown).trim();
      } else if (turn.el) {
        body = elementToMarkdown(turn.el).trim();
      } else if (turn.html) {
        body = global.MdToDocxHtml.htmlToMarkdown(turn.html).trim();
      }
      if (!body) continue;
      parts.push(heading, "", body, "");
    }
    return parts.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function selectionToMarkdown() {
    const sel = global.getSelection && global.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return "";
    const range = sel.getRangeAt(0);
    const container = document.createElement("div");
    container.appendChild(range.cloneContents());
    const md = global.MdToDocxHtml.htmlToMarkdown(container.innerHTML).trim();
    if (md) return md;
    return (sel.toString() || "").trim();
  }

  function scoreTextLength(el) {
    if (!el || !el.innerText) return 0;
    return el.innerText.replace(/\s+/g, " ").trim().length;
  }

  function stripNoise(root) {
    if (!root || !root.querySelectorAll) return root;
    root
      .querySelectorAll("nav, aside, footer, script, style, noscript, svg, iframe, template")
      .forEach((el) => el.remove());
    return root;
  }

  function extractPageMarkdown(document) {
    const fromSel = selectionToMarkdown();
    if (fromSel) {
      return global.MdToDocxHtml.beautifyMarkdown
        ? global.MdToDocxHtml.beautifyMarkdown(fromSel)
        : fromSel;
    }

    const candidates = [
      document.querySelector("article"),
      document.querySelector("main"),
      document.querySelector("[role='main']"),
      document.querySelector(".post-content, .article-content, .entry-content, #content"),
    ].filter(Boolean);

    let best = candidates[0] || null;
    let bestScore = best ? scoreTextLength(best) : 0;
    for (const el of candidates) {
      const score = scoreTextLength(el);
      if (score > bestScore) {
        best = el;
        bestScore = score;
      }
    }

    if (!best || bestScore < 80) {
      const blocks = Array.from(
        document.querySelectorAll("article, main, section, div")
      ).filter((el) => scoreTextLength(el) > 200);
      for (const el of blocks) {
        const score = scoreTextLength(el);
        if (score > bestScore && el !== document.body) {
          best = el;
          bestScore = score;
        }
      }
    }

    if (!best) best = document.body;
    const clone = best.cloneNode(true);
    stripNoise(clone);
    return elementToMarkdown(clone).trim();
  }

  global.MdToDocxExtract = {
    sanitizeTitle,
    elementToMarkdown,
    findLatestAssistant,
    turnsToMarkdown,
    selectionToMarkdown,
    extractPageMarkdown,
  };
})(typeof window !== "undefined" ? window : globalThis);
