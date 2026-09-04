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

  // SPA pages (e.g. Zhihu) may wipe body after idle; retry covers the race
  // before the shared remount observer is attached.
  setTimeout(setup, 1000);
  setTimeout(setup, 3000);

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { exportPage };
  }
})();
