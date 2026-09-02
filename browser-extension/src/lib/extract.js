(function (global) {
  function sanitizeTitle(title) {
    return (title || "document")
      .replace(/[<>:"/\\|?*]/g, "")
      .replace(/\s+/g, "_")
      .slice(0, 80) || "document";
  }

  function elementToMarkdown(el) {
    if (!el) return "";
    return global.MdToDocxHtml.htmlToMarkdown(el.innerHTML);
  }

  function findLatestAssistant(nodes, selectors) {
    for (const sel of selectors) {
      const list = document.querySelectorAll(sel);
      if (list.length) return list[list.length - 1];
    }
    return null;
  }

  global.MdToDocxExtract = {
    sanitizeTitle,
    elementToMarkdown,
    findLatestAssistant,
  };
})(typeof window !== "undefined" ? window : globalThis);
