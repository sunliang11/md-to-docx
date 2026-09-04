(function () {
  function exportPage() {
    const markdown = MdToDocxExtract.extractPageMarkdown(document);
    if (!markdown || !markdown.trim()) {
      MdToDocxExport.showToast("Could not find exportable content on this page");
      return;
    }
    const title = document.title || "webpage";
    MdToDocxExport.convertAndDownload(markdown, title);
  }

  function setup() {
    MdToDocxExport.injectFloatingButton(exportPage);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { exportPage };
  }
})();
