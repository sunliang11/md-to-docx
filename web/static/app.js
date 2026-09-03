(function () {
  const markdownEl = document.getElementById("markdown");
  const previewEl = document.getElementById("preview");
  const presetEl = document.getElementById("preset");
  const tocEl = document.getElementById("toc");
  const numberingEl = document.getElementById("numbering");
  const pageNumbersEl = document.getElementById("page-numbers");
  const exampleEl = document.getElementById("example");
  const generateBtn = document.getElementById("generate");
  const validateBtn = document.getElementById("validate");
  const copyCliBtn = document.getElementById("copy-cli");
  const errorEl = document.getElementById("error");
  const errorProblem = document.getElementById("error-problem");
  const errorCause = document.getElementById("error-cause");
  const errorFix = document.getElementById("error-fix");
  const errorDismiss = document.getElementById("error-dismiss");
  const charCountEl = document.getElementById("char-count");
  const toastEl = document.getElementById("toast");
  const presetHintEl = document.getElementById("preset-hint");
  const previewPresetEl = document.getElementById("preview-preset");
  const langEnBtn = document.getElementById("lang-en");
  const langZhBtn = document.getElementById("lang-zh");
  const optionsPanel = document.getElementById("options-panel");
  const toggleOptions = document.getElementById("toggle-options");
  const templateEl = document.getElementById("community-template");
  const titleEl = document.getElementById("doc-title");
  const authorEl = document.getElementById("doc-author");
  const dateEl = document.getElementById("doc-date");
  const validatePanel = document.getElementById("validate-panel");
  const validateList = document.getElementById("validate-list");
  const validateMeta = document.getElementById("validate-meta");
  const reverseFile = document.getElementById("reverse-file");
  const reverseOut = document.getElementById("reverse-out");
  const runReverse = document.getElementById("run-reverse");
  const sendToConvert = document.getElementById("send-to-convert");
  const copyReverseMd = document.getElementById("copy-reverse-md");
  const copyCliReverse = document.getElementById("copy-cli-reverse");
  const diffA = document.getElementById("diff-a");
  const diffB = document.getElementById("diff-b");
  const diffOut = document.getElementById("diff-out");
  const diffFormat = document.getElementById("diff-format");
  const runDiff = document.getElementById("run-diff");
  const loadDiffSample = document.getElementById("load-diff-sample");
  const copyCliDiff = document.getElementById("copy-cli-diff");
  const diffFileA = document.getElementById("diff-file-a");
  const diffFileB = document.getElementById("diff-file-b");

  const SNIPPETS = {
    frontmatter: "---\ntitle: Playground sample\nauthor: Demo\ndate: 2026-09-03\n---\n\n",
    callout: ":::warning\nImportant caution text.\n:::\n\n",
    pagebreak: "<!-- pagebreak -->\n\n",
    caption: "![Architecture](https://placehold.co/640x240/png){#fig:arch}\n\nSee [@fig:arch].\n\n",
    mermaid: "```mermaid\nflowchart LR\n  A[Markdown] --> B[DOCX]\n```\n\n",
    math: "Inline $E = mc^2$ and a block:\n\n$$\n\\int_0^1 x^2 \\, dx\n$$\n\n",
  };

  const DIFF_SAMPLE_A = "# Status\n\nShip the compiler.\n\n## Scope\n\nConvert Markdown to DOCX.\n";
  const DIFF_SAMPLE_B = "# Status\n\nShip the native compiler.\n\n## Scope\n\nConvert Markdown to DOCX and reverse it.\n\n:::note\nDiff is structural, not a word-level redline.\n:::\n";

  let debounceTimer;
  let toastTimer;
  let previewSeq = 0;
  let presetsCache = [];
  let currentMode = "convert";
  let optionsOpen = false;
  let currentLang =
    localStorage.getItem("md-to-docx-lang") ||
    (navigator.language.startsWith("zh") ? "zh" : "en");
  let lastErrorDetail = null;

  const FONT_FALLBACKS = {
    Calibri: "Calibri, sans-serif",
    Georgia: "Georgia, serif",
    "Times New Roman": '"Times New Roman", Times, serif',
    "Microsoft YaHei": '"Microsoft YaHei", "PingFang SC", sans-serif',
    SimSun: "SimSun, STSong, serif",
    KaiTi: "KaiTi, STKaiti, serif",
  };

  function messages() {
    return window.MD_TO_DOCX_I18N[currentLang] || window.MD_TO_DOCX_I18N.en;
  }

  function t(key, vars) {
    const m = messages();
    let text = m[key];
    if (text === undefined) return key;
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        text = text.replace("{" + k + "}", vars[k]);
      });
    }
    return text;
  }

  function presetDescription(name) {
    const desc = messages().presetDescriptions[name];
    return desc || name;
  }

  function formatBytes(n) {
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / (1024 * 1024)).toFixed(1) + " MB";
  }

  function previewFontFamily(latin, eastAsia) {
    const latinStack = FONT_FALLBACKS[latin] || latin + ", sans-serif";
    const eastStack = FONT_FALLBACKS[eastAsia] || eastAsia + ", sans-serif";
    return latinStack + ", " + eastStack;
  }

  function getPresetByName(name) {
    return presetsCache.find(function (p) {
      return p.name === name;
    });
  }

  function parseError(res, json) {
    const detail = (json && (json.detail || json)) || {};
    if (typeof detail === "string") {
      return { problem: "Request failed", cause: detail, fix: "Try again" };
    }
    if (Array.isArray(detail)) {
      return { problem: "Request failed", cause: JSON.stringify(detail), fix: "Try again" };
    }
    return {
      problem: detail.problem || "Request failed",
      cause: detail.cause || res.statusText,
      fix: detail.fix || "Try again",
    };
  }

  function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll(".mode-nav__btn").forEach(function (btn) {
      btn.classList.toggle("mode-nav__btn--active", btn.getAttribute("data-mode") === mode);
    });
    document.querySelectorAll("[data-mode-panel]").forEach(function (el) {
      const on = el.getAttribute("data-mode-panel") === mode;
      el.classList.toggle("hidden", !on);
      if (el.hasAttribute("hidden") || el.tagName === "MAIN") {
        el.hidden = !on;
      }
    });
    document.querySelector(".skip-link").setAttribute("href", "#workspace-" + mode);
    showError(null);
    if (mode === "convert") {
      if (!optionsOpen) optionsPanel.classList.add("hidden");
      if (!validateList.children.length) validatePanel.classList.add("hidden");
      schedulePreview();
    }
  }

  function applyI18n() {
    document.title = t("pageTitle");
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";

    document.getElementById("i18n-header-hint").textContent = t("headerHint");
    document.getElementById("lang-switch").setAttribute("aria-label", t("langLabel"));
    document.getElementById("mode-convert").textContent = t("modeConvert");
    document.getElementById("mode-reverse").textContent = t("modeReverse");
    document.getElementById("mode-diff").textContent = t("modeDiff");
    document.getElementById("i18n-label-example").textContent = t("labelExample");
    document.getElementById("i18n-label-preset").textContent = t("labelPreset");
    document.getElementById("i18n-label-toc").textContent = t("labelToc");
    document.getElementById("i18n-label-numbering").textContent = t("labelNumbering");
    document.getElementById("i18n-label-title").textContent = t("labelTitle");
    document.getElementById("i18n-label-author").textContent = t("labelAuthor");
    document.getElementById("i18n-label-date").textContent = t("labelDate");
    document.getElementById("i18n-label-template").textContent = t("labelTemplate");
    document.getElementById("i18n-template-none").textContent = t("templateNone");
    document.getElementById("i18n-label-page-numbers").textContent = t("labelPageNumbers");
    document.getElementById("i18n-snippets-label").textContent = t("snippetsLabel");
    document.getElementById("i18n-example-placeholder").textContent = t("examplePlaceholder");
    document.getElementById("i18n-pane-markdown").textContent = t("paneMarkdown");
    document.getElementById("i18n-pane-preview").textContent = t("panePreview");
    document.getElementById("i18n-badge-approx").textContent = t("badgeApproximation");
    document.getElementById("i18n-footer-privacy").textContent = t("footerPrivacy");
    document.getElementById("i18n-label-docx").textContent = t("labelDocx");
    document.getElementById("i18n-label-diff-format").textContent = t("labelDiffFormat");
    document.getElementById("i18n-pane-reverse-in").textContent = t("paneReverseIn");
    document.getElementById("i18n-pane-reverse-out").textContent = t("paneReverseOut");
    document.getElementById("i18n-pane-diff-a").textContent = t("paneDiffA");
    document.getElementById("i18n-pane-diff-b").textContent = t("paneDiffB");
    document.getElementById("i18n-pane-diff-out").textContent = t("paneDiffOut");
    document.getElementById("i18n-upload-a").textContent = t("uploadA");
    document.getElementById("i18n-upload-b").textContent = t("uploadB");
    document.getElementById("i18n-reverse-empty").textContent = t("reverseEmpty");
    document.getElementById("i18n-validate-title").textContent = t("validateTitle");
    markdownEl.placeholder = t("placeholderMarkdown");
    reverseOut.placeholder = t("placeholderReverse");
    diffA.placeholder = t("diffEmpty");
    diffB.placeholder = t("diffEmpty");
    if (!diffOut.textContent.trim()) diffOut.textContent = t("diffEmpty");

    toggleOptions.textContent = optionsOpen ? t("btnOptionsHide") : t("btnOptions");
    copyCliBtn.textContent = t("btnCopyCli");
    copyCliReverse.textContent = t("btnCopyCli");
    copyCliDiff.textContent = t("btnCopyCli");
    sendToConvert.textContent = t("btnSendConvert");
    copyReverseMd.textContent = t("btnCopy");
    loadDiffSample.textContent = t("btnLoadSample");
    if (!generateBtn.classList.contains("btn--loading")) {
      generateBtn.querySelector(".btn__label").textContent = t("btnExport");
    }
    if (!validateBtn.classList.contains("btn--loading")) {
      validateBtn.querySelector(".btn__label").textContent = t("btnValidate");
    }
    if (!runReverse.classList.contains("btn--loading")) {
      runReverse.querySelector(".btn__label").textContent = t("btnReverse");
    }
    if (!runDiff.classList.contains("btn--loading")) {
      runDiff.querySelector(".btn__label").textContent = t("btnDiff");
    }
    errorDismiss.setAttribute("aria-label", t("errorDismiss"));

    langEnBtn.classList.toggle("lang-switch__btn--active", currentLang === "en");
    langZhBtn.classList.toggle("lang-switch__btn--active", currentLang === "zh");

    exampleEl.querySelectorAll("option[data-example-key]").forEach(function (opt) {
      const key = opt.getAttribute("data-example-key");
      opt.textContent = messages().exampleOptions[key] || key;
    });

    document.querySelectorAll("[data-snippet]").forEach(function (btn) {
      const key = btn.getAttribute("data-snippet");
      const map = {
        frontmatter: "snippetFrontmatter",
        callout: "snippetCallout",
        pagebreak: "snippetPagebreak",
        caption: "snippetCaption",
        mermaid: "snippetMermaid",
        math: "snippetMath",
      };
      btn.textContent = t(map[key]);
    });

    rebuildPresetOptions();
    if (lastErrorDetail) showError(lastErrorDetail);
    if (presetEl.value) applyPresetUi(presetEl.value, false);
    if (currentMode === "convert") schedulePreview();
  }

  function setLang(lang) {
    currentLang = lang;
    localStorage.setItem("md-to-docx-lang", lang);
    applyI18n();
  }

  function rebuildPresetOptions() {
    const selected = presetEl.value;
    presetEl.innerHTML = "";
    presetsCache.forEach(function (p) {
      const opt = document.createElement("option");
      opt.value = p.name;
      opt.textContent = p.name + " — " + presetDescription(p.name);
      presetEl.appendChild(opt);
    });
    if (selected && presetsCache.some(function (p) { return p.name === selected; })) {
      presetEl.value = selected;
    }
  }

  function applyPresetUi(name, syncChecks) {
    const preset = getPresetByName(name);
    if (!preset) return;

    if (syncChecks !== false) {
      tocEl.checked = preset.toc;
      numberingEl.checked = preset.numbering;
    }

    previewPresetEl.textContent = preset.name;

    const pv = preset.preview || {};
    const latin = pv.latin || "Calibri";
    const eastAsia = pv.east_asia || "Microsoft YaHei";
    const bodyPt = pv.body_pt || 11;
    const headingColor = pv.heading_color || "#111827";

    previewEl.style.setProperty("--preview-font-body", previewFontFamily(latin, eastAsia));
    previewEl.style.setProperty("--preview-body-pt", bodyPt + "px");
    previewEl.style.setProperty("--preview-heading-color", headingColor);

    const parts = [
      preset.name,
      t("presetHintFonts", { latin: latin, east_asia: eastAsia, pt: String(bodyPt) }),
      tocEl.checked ? t("presetHintTocOn") : t("presetHintTocOff"),
      numberingEl.checked ? t("presetHintNumberingOn") : t("presetHintNumberingOff"),
    ];
    if (pv.header) parts.push(t("presetHintHeader", { header: pv.header }));
    presetHintEl.textContent = parts.join(" · ");
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    toastEl.textContent = message;
    toastEl.classList.remove("hidden");
    toastEl.classList.add("toast--visible");
    toastTimer = setTimeout(function () {
      toastEl.classList.remove("toast--visible");
    }, 3000);
  }

  function showError(detail) {
    lastErrorDetail = detail;
    if (!detail) {
      errorEl.classList.add("hidden");
      errorProblem.textContent = "";
      errorCause.textContent = "";
      errorFix.textContent = "";
      return;
    }
    errorProblem.textContent = detail.problem ? detail.problem : "";
    errorCause.textContent = detail.cause ? t("errorCause") + detail.cause : "";
    errorFix.textContent = detail.fix ? t("errorFix") + detail.fix : "";
    errorEl.classList.remove("hidden");
  }

  function setBtnLoading(btn, loading, idleKey, loadingKey) {
    btn.disabled = loading;
    btn.classList.toggle("btn--loading", loading);
    const label = btn.querySelector(".btn__label");
    if (label) label.textContent = loading ? t(loadingKey) : t(idleKey);
  }

  function convertPayload() {
    const payload = {
      markdown: markdownEl.value,
      preset: presetEl.value,
      toc: tocEl.checked,
      numbering: numberingEl.checked,
      page_numbers: pageNumbersEl.checked,
    };
    if (titleEl.value.trim()) payload.title = titleEl.value.trim();
    if (authorEl.value.trim()) payload.author = authorEl.value.trim();
    if (dateEl.value.trim()) payload.date = dateEl.value.trim();
    if (templateEl.value) payload.template = templateEl.value;
    return payload;
  }

  function convertCli() {
    const parts = ["./bin/convert report.md --preset " + presetEl.value];
    parts.push(tocEl.checked ? "--toc" : "--no-toc");
    if (numberingEl.checked) parts.push("--numbering");
    if (!pageNumbersEl.checked) parts.push("--no-page-numbers");
    if (titleEl.value.trim()) parts.push("--title " + JSON.stringify(titleEl.value.trim()));
    if (authorEl.value.trim()) parts.push("--author " + JSON.stringify(authorEl.value.trim()));
    if (dateEl.value.trim()) parts.push("--date " + JSON.stringify(dateEl.value.trim()));
    if (templateEl.value) {
      parts.push("--template templates/" + templateEl.value + "/template.docx");
    }
    return parts.join(" ");
  }

  function updateCharCount() {
    const bytes = new TextEncoder().encode(markdownEl.value).length;
    charCountEl.textContent = formatBytes(bytes);
  }

  function showPreviewEmpty() {
    previewEl.innerHTML = "";
    previewEl.classList.add("preview--empty");
    previewEl.textContent = t("previewEmpty");
  }

  function schedulePreview() {
    updateCharCount();
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(fetchPreview, 350);
  }

  async function fetchPreview() {
    const text = markdownEl.value;
    if (!text.trim()) {
      showPreviewEmpty();
      return;
    }
    const seq = ++previewSeq;
    previewEl.classList.remove("preview--empty");
    previewEl.classList.add("preview--loading");
    try {
      const res = await fetch("/api/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ markdown: text, numbering: numberingEl.checked }),
      });
      if (seq !== previewSeq) return;
      if (!res.ok) {
        previewEl.classList.remove("preview--loading");
        previewEl.textContent = text;
        return;
      }
      const data = await res.json();
      if (seq !== previewSeq) return;
      previewEl.classList.remove("preview--loading");
      if (!data.html) {
        showPreviewEmpty();
        return;
      }
      previewEl.innerHTML = data.html;
      if (data.css && !document.getElementById("engine-preview-css")) {
        const style = document.createElement("style");
        style.id = "engine-preview-css";
        style.textContent = data.css;
        document.head.appendChild(style);
      }
    } catch (_) {
      if (seq !== previewSeq) return;
      previewEl.classList.remove("preview--loading");
      previewEl.textContent = text;
    }
  }

  async function loadPresets() {
    const res = await fetch("/api/presets");
    const data = await res.json();
    presetsCache = data.presets;
    rebuildPresetOptions();
    presetEl.value = "technical";
    applyPresetUi("technical");
  }

  async function loadTemplates() {
    try {
      const res = await fetch("/api/templates");
      const data = await res.json();
      (data.templates || []).forEach(function (tpl) {
        const opt = document.createElement("option");
        opt.value = tpl.id;
        opt.textContent = tpl.name;
        templateEl.appendChild(opt);
      });
    } catch (_) {
      /* community templates optional */
    }
  }

  async function loadExample(name) {
    if (!name) return;
    showError(null);
    try {
      const res = await fetch("/examples/" + name + ".md");
      if (!res.ok) throw new Error("failed to load example");
      markdownEl.value = await res.text();
      schedulePreview();
      const label = exampleEl.options[exampleEl.selectedIndex].textContent;
      showToast(t("toastLoaded", { name: label }));
    } catch (e) {
      exampleEl.value = "";
      showError({
        problem: t("errorExampleLoad"),
        cause: String(e),
        fix: t("errorExampleFix"),
      });
    }
  }

  async function generateDocx() {
    showError(null);
    setBtnLoading(generateBtn, true, "btnExport", "btnExportLoading");
    try {
      const res = await fetch("/api/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(convertPayload()),
      });
      if (!res.ok) {
        let json = {};
        try { json = await res.json(); } catch (_) {}
        showError(parseError(res, json));
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "document.docx";
      a.click();
      URL.revokeObjectURL(url);
      showToast(t("toastDownloaded"));
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(generateBtn, false, "btnExport", "btnExportLoading");
    }
  }

  async function runValidate() {
    showError(null);
    setBtnLoading(validateBtn, true, "btnValidate", "btnValidateLoading");
    try {
      const res = await fetch("/api/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ markdown: markdownEl.value, strict: false }),
      });
      const json = await res.json();
      if (!res.ok) {
        showError(parseError(res, json));
        return;
      }
      const issues = json.issues || [];
      validateList.innerHTML = "";
      validatePanel.classList.remove("hidden");
      if (!issues.length) {
        validateMeta.textContent = t("validateClean");
        const li = document.createElement("li");
        li.className = "validate-list__ok";
        li.textContent = t("validateClean");
        validateList.appendChild(li);
      } else {
        validateMeta.textContent = t("validateCount", { n: String(issues.length) });
        issues.forEach(function (issue) {
          const li = document.createElement("li");
          li.className = "validate-list__item validate-list__item--" + issue.severity;
          const line = issue.line != null ? "L" + issue.line + " · " : "";
          li.textContent = line + issue.code + ": " + issue.message;
          if (issue.line != null) {
            li.tabIndex = 0;
            li.addEventListener("click", function () {
              jumpToLine(issue.line);
            });
          }
          validateList.appendChild(li);
        });
      }
      showToast(t("toastValidated"));
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(validateBtn, false, "btnValidate", "btnValidateLoading");
    }
  }

  function jumpToLine(line) {
    const lines = markdownEl.value.split("\n");
    let pos = 0;
    for (let i = 0; i < line - 1 && i < lines.length; i++) {
      pos += lines[i].length + 1;
    }
    markdownEl.focus();
    markdownEl.setSelectionRange(pos, pos);
    const ratio = (line - 1) / Math.max(lines.length, 1);
    markdownEl.scrollTop = ratio * markdownEl.scrollHeight;
  }

  function insertSnippet(key) {
    const block = SNIPPETS[key];
    if (!block) return;
    const start = markdownEl.selectionStart;
    const end = markdownEl.selectionEnd;
    const value = markdownEl.value;
    markdownEl.value = value.slice(0, start) + block + value.slice(end);
    markdownEl.focus();
    const cursor = start + block.length;
    markdownEl.setSelectionRange(cursor, cursor);
    schedulePreview();
    showToast(t("toastSnippet", { name: document.querySelector('[data-snippet="' + key + '"]').textContent }));
  }

  async function doReverse() {
    showError(null);
    const file = reverseFile.files && reverseFile.files[0];
    if (!file) {
      showError({ problem: t("errorNoFile"), cause: "no upload", fix: t("errorNoFileFix") });
      return;
    }
    setBtnLoading(runReverse, true, "btnReverse", "btnReverseLoading");
    try {
      const fd = new FormData();
      fd.append("file", file, file.name);
      const res = await fetch("/api/reverse", { method: "POST", body: fd });
      if (!res.ok) {
        let json = {};
        try { json = await res.json(); } catch (_) {}
        showError(parseError(res, json));
        return;
      }
      reverseOut.value = await res.text();
      sendToConvert.disabled = !reverseOut.value.trim();
      copyReverseMd.disabled = !reverseOut.value.trim();
      showToast(t("toastReversed"));
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(runReverse, false, "btnReverse", "btnReverseLoading");
    }
  }

  async function doDiff() {
    showError(null);
    const a = diffA.value;
    const b = diffB.value;
    const fileA = diffFileA.files && diffFileA.files[0];
    const fileB = diffFileB.files && diffFileB.files[0];
    setBtnLoading(runDiff, true, "btnDiff", "btnDiffLoading");
    try {
      let res;
      if (fileA && fileB) {
        const fd = new FormData();
        fd.append("a", fileA, fileA.name);
        fd.append("b", fileB, fileB.name);
        fd.append("format", diffFormat.value);
        res = await fetch("/api/diff/files", { method: "POST", body: fd });
      } else {
        if (!a.trim() && !b.trim()) {
          showError({ problem: t("errorDiffEmpty"), cause: "empty", fix: t("errorDiffEmptyFix") });
          return;
        }
        res = await fetch("/api/diff", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ a: a, b: b, format: diffFormat.value }),
        });
      }
      if (!res.ok) {
        let json = {};
        try { json = await res.json(); } catch (_) {}
        showError(parseError(res, json));
        return;
      }
      diffOut.textContent = await res.text();
      showToast(t("toastDiffed"));
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(runDiff, false, "btnDiff", "btnDiffLoading");
    }
  }

  function copyText(text) {
    navigator.clipboard.writeText(text).then(function () {
      showToast(t("toastCopied"));
    }).catch(function () {
      showError({ problem: t("errorCopy"), cause: "Clipboard access denied", fix: t("errorCopyFix") });
    });
  }

  markdownEl.addEventListener("input", schedulePreview);
  numberingEl.addEventListener("change", function () {
    applyPresetUi(presetEl.value, false);
    schedulePreview();
  });
  tocEl.addEventListener("change", function () {
    applyPresetUi(presetEl.value, false);
  });

  errorDismiss.addEventListener("click", function () { showError(null); });

  presetEl.addEventListener("change", function () {
    applyPresetUi(presetEl.value);
    schedulePreview();
  });

  langEnBtn.addEventListener("click", function () { setLang("en"); });
  langZhBtn.addEventListener("click", function () { setLang("zh"); });

  exampleEl.addEventListener("change", function () { loadExample(exampleEl.value); });
  generateBtn.addEventListener("click", generateDocx);
  validateBtn.addEventListener("click", runValidate);

  toggleOptions.addEventListener("click", function () {
    optionsOpen = !optionsOpen;
    optionsPanel.classList.toggle("hidden", !optionsOpen);
    toggleOptions.setAttribute("aria-expanded", optionsOpen ? "true" : "false");
    toggleOptions.textContent = optionsOpen ? t("btnOptionsHide") : t("btnOptions");
  });

  document.querySelectorAll("[data-snippet]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      insertSnippet(btn.getAttribute("data-snippet"));
    });
  });

  document.querySelectorAll(".mode-nav__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setMode(btn.getAttribute("data-mode"));
    });
  });

  copyCliBtn.addEventListener("click", function () { copyText(convertCli()); });
  copyCliReverse.addEventListener("click", function () {
    copyText("md-to-docx reverse input.docx -o report.md");
  });
  copyCliDiff.addEventListener("click", function () {
    copyText("md-to-docx diff a.md b.md --format " + diffFormat.value);
  });

  runReverse.addEventListener("click", doReverse);
  reverseFile.addEventListener("change", function () {
    if (reverseFile.files && reverseFile.files[0]) doReverse();
  });
  copyReverseMd.addEventListener("click", function () {
    if (!reverseOut.value) return;
    navigator.clipboard.writeText(reverseOut.value).then(function () {
      showToast(t("toastCopiedMd"));
    });
  });
  sendToConvert.addEventListener("click", function () {
    if (!reverseOut.value.trim()) return;
    markdownEl.value = reverseOut.value;
    setMode("convert");
    schedulePreview();
    showToast(t("toastSentConvert"));
  });

  runDiff.addEventListener("click", doDiff);
  loadDiffSample.addEventListener("click", function () {
    diffA.value = DIFF_SAMPLE_A;
    diffB.value = DIFF_SAMPLE_B;
    diffFileA.value = "";
    diffFileB.value = "";
    showToast(t("toastSample"));
    doDiff();
  });

  async function fillFromUpload(input, target) {
    const file = input.files && input.files[0];
    if (!file) return;
    if (file.name.toLowerCase().endsWith(".md")) {
      target.value = await file.text();
    }
  }
  diffFileA.addEventListener("change", function () { fillFromUpload(diffFileA, diffA); });
  diffFileB.addEventListener("change", function () { fillFromUpload(diffFileB, diffB); });

  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (currentMode === "convert" && !generateBtn.disabled) generateDocx();
      if (currentMode === "reverse" && !runReverse.disabled) doReverse();
      if (currentMode === "diff" && !runDiff.disabled) doDiff();
    }
  });

  Promise.all([loadPresets(), loadTemplates()]).then(function () {
    applyI18n();
    markdownEl.value = currentLang === "zh"
      ? "# 技术报告\n\n在此粘贴 AI 生成的 Markdown。\n"
      : "# Technical Report\n\nPaste AI-generated Markdown here.\n";
    setMode("convert");
    schedulePreview();
  });
})();
