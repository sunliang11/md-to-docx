/* Simple HTML → Markdown (whitelist tags) with block spacing + beautify. */
(function (global) {
  function escapeText(text) {
    return text.replace(/\s+/g, " ").trim();
  }

  function collapseText(text) {
    return text.replace(/[ \t\f\v]+/g, " ").replace(/\n+/g, " ");
  }

  function wrapBlock(inner) {
    const body = String(inner || "").trim();
    if (!body) return "";
    return "\n\n" + body + "\n\n";
  }

  function nodeToMd(node, listDepth) {
    if (node.nodeType === Node.TEXT_NODE) {
      return collapseText(node.textContent || "");
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return "";

    const tag = node.tagName.toLowerCase();

    if (
      tag === "script" ||
      tag === "style" ||
      tag === "noscript" ||
      tag === "svg" ||
      tag === "nav" ||
      tag === "iframe" ||
      tag === "template"
    ) {
      return "";
    }

    if (tag === "hr") return "\n\n---\n\n";

    const children = Array.from(node.childNodes)
      .map((c) => nodeToMd(c, listDepth))
      .join("");

    switch (tag) {
      case "h1":
        return wrapBlock("# " + escapeText(children));
      case "h2":
        return wrapBlock("## " + escapeText(children));
      case "h3":
        return wrapBlock("### " + escapeText(children));
      case "h4":
        return wrapBlock("#### " + escapeText(children));
      case "h5":
        return wrapBlock("##### " + escapeText(children));
      case "h6":
        return wrapBlock("###### " + escapeText(children));
      case "p":
        return wrapBlock(children.trim());
      case "br":
        return "\n";
      case "strong":
      case "b":
        return "**" + children.trim() + "**";
      case "em":
      case "i":
        return "*" + children.trim() + "*";
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
        return wrapBlock("```" + lang + "\n" + body.replace(/\n$/, "") + "\n```");
      }
      case "ul":
        return (
          "\n\n" +
          Array.from(node.children)
            .filter((li) => li.tagName === "LI")
            .map((li) => "- " + nodeToMd(li, listDepth + 1).trim())
            .join("\n") +
          "\n\n"
        );
      case "ol":
        return (
          "\n\n" +
          Array.from(node.children)
            .filter((li) => li.tagName === "LI")
            .map((li, i) => i + 1 + ". " + nodeToMd(li, listDepth + 1).trim())
            .join("\n") +
          "\n\n"
        );
      case "li":
        return children;
      case "blockquote":
        return wrapBlock(
          "> " + children.trim().replace(/\n+/g, "\n").replace(/\n/g, "\n> ")
        );
      case "a": {
        const href = node.getAttribute("href") || "";
        const label = escapeText(children);
        if (!label && !href) return "";
        return "[" + label + "](" + href + ")";
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
          const cells = Array.from(tr.querySelectorAll("th, td")).map((c) =>
            escapeText(c.textContent)
          );
          return "| " + cells.join(" | ") + " |";
        });
        if (lines.length > 1) {
          const sep =
            "| " +
            lines[0]
              .split("|")
              .slice(1, -1)
              .map(() => "---")
              .join(" | ") +
            " |";
          lines.splice(1, 0, sep);
        }
        return wrapBlock(lines.join("\n"));
      }
      case "div":
      case "section":
      case "article":
      case "header":
      case "footer":
      case "aside":
      case "figure":
      case "figcaption":
      case "main":
      case "details":
      case "summary":
        return wrapBlock(children);
      case "thead":
      case "tbody":
      case "tr":
      case "th":
      case "td":
      case "span":
      case "label":
        return children;
      default:
        return children;
    }
  }

  function beautifyMarkdown(md) {
    let out = String(md || "");
    out = out.replace(/[ \t]+\n/g, "\n");
    out = out.replace(/\*\*\s*\*\*/g, "");
    out = out.replace(/\[\s*\]\(\s*\)/g, "");
    out = out.replace(/!\[\s*\]\(\s*\)/g, "");
    // Ensure blank line before headings / fences / lists when jammed
    out = out.replace(/([^\n])\n(#{1,6} )/g, "$1\n\n$2");
    out = out.replace(/([^\n])\n(```)/g, "$1\n\n$2");
    out = out.replace(/([^\n])\n([-*+] )/g, "$1\n\n$2");
    out = out.replace(/([^\n])\n(\d+\. )/g, "$1\n\n$2");
    // Blank line after headings
    out = out.replace(/(^#{1,6} .+)\n([^\n#])/gm, "$1\n\n$2");
    out = out.replace(/\n{3,}/g, "\n\n");
    return out.trim();
  }

  function htmlToMarkdown(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    return beautifyMarkdown(nodeToMd(doc.body, 0));
  }

  global.MdToDocxHtml = { htmlToMarkdown, beautifyMarkdown };
})(typeof window !== "undefined" ? window : globalThis);
