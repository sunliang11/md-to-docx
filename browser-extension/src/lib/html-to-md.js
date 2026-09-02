/* Simple HTML → Markdown (whitelist tags). */
(function (global) {
  function escapeText(text) {
    return text.replace(/\s+/g, " ").trim();
  }

  function nodeToMd(node, listDepth) {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.textContent;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return "";

    const tag = node.tagName.toLowerCase();
    const children = Array.from(node.childNodes).map((c) => nodeToMd(c, listDepth)).join("");

    switch (tag) {
      case "h1": return "\n\n# " + escapeText(children) + "\n\n";
      case "h2": return "\n\n## " + escapeText(children) + "\n\n";
      case "h3": return "\n\n### " + escapeText(children) + "\n\n";
      case "h4": return "\n\n#### " + escapeText(children) + "\n\n";
      case "h5": return "\n\n##### " + escapeText(children) + "\n\n";
      case "h6": return "\n\n###### " + escapeText(children) + "\n\n";
      case "p": return "\n\n" + children.trim() + "\n\n";
      case "br": return "\n";
      case "strong", "b": return "**" + children.trim() + "**";
      case "em", "i": return "*" + children.trim() + "*";
      case "code":
        if (node.parentElement && node.parentElement.tagName === "PRE") return children;
        return "`" + children.trim() + "`";
      case "pre": {
        const code = node.querySelector("code");
        let lang = "";
        if (code && code.className) {
          const m = code.className.match(/language-(\w+)/);
          if (m) lang = m[1];
        }
        const body = code ? code.textContent : node.textContent;
        return "\n\n```" + lang + "\n" + body.replace(/\n$/, "") + "\n```\n\n";
      }
      case "ul":
        return "\n" + Array.from(node.children)
          .filter((li) => li.tagName === "LI")
          .map((li) => "- " + nodeToMd(li, listDepth + 1).trim())
          .join("\n") + "\n\n";
      case "ol":
        return "\n" + Array.from(node.children)
          .filter((li) => li.tagName === "LI")
          .map((li, i) => (i + 1) + ". " + nodeToMd(li, listDepth + 1).trim())
          .join("\n") + "\n\n";
      case "li": return children;
      case "blockquote": return "\n\n> " + children.trim().replace(/\n/g, "\n> ") + "\n\n";
      case "a": {
        const href = node.getAttribute("href") || "";
        return "[" + escapeText(children) + "](" + href + ")";
      }
      case "img": {
        const alt = node.getAttribute("alt") || "image";
        const src = node.getAttribute("src") || "";
        return "![" + alt + "](" + src + ")";
      }
      case "table": {
        const rows = Array.from(node.querySelectorAll("tr"));
        if (!rows.length) return "";
        const lines = rows.map((tr) => {
          const cells = Array.from(tr.querySelectorAll("th, td")).map((c) => escapeText(c.textContent));
          return "| " + cells.join(" | ") + " |";
        });
        if (lines.length > 1) {
          const sep = "| " + lines[0].split("|").slice(1, -1).map(() => "---").join(" | ") + " |";
          lines.splice(1, 0, sep);
        }
        return "\n\n" + lines.join("\n") + "\n\n";
      }
      case "thead", "tbody", "tr", "th", "td", "div", "span", "section", "article":
        return children;
      default:
        return children;
    }
  }

  function htmlToMarkdown(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    return nodeToMd(doc.body, 0).replace(/\n{3,}/g, "\n\n").trim();
  }

  global.MdToDocxHtml = { htmlToMarkdown };
})(typeof window !== "undefined" ? window : globalThis);
