(function () {
  const markdownEl = document.getElementById("markdown");
  const previewEl = document.getElementById("preview");
  const presetEl = document.getElementById("preset");
  const batchPresetEl = document.getElementById("batch-preset");
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
  const templateFileEl = document.getElementById("template-file");
  const titleEl = document.getElementById("doc-title");
  const authorEl = document.getElementById("doc-author");
  const dateEl = document.getElementById("doc-date");
  const versionEl = document.getElementById("doc-version");
  const tocTitleEl = document.getElementById("toc-title");
  const figureLabelEl = document.getElementById("figure-label");
  const tableLabelEl = document.getElementById("table-label");
  const sectionLabelEl = document.getElementById("section-label");
  const normalizeEl = document.getElementById("normalize");
  const noPluginsEl = document.getElementById("no-plugins");
  const strictMermaidEl = document.getElementById("strict-mermaid");
  const validateStrictEl = document.getElementById("validate-strict");
  const validatePanel = document.getElementById("validate-panel");
  const validateList = document.getElementById("validate-list");
  const validateMeta = document.getElementById("validate-meta");
  const convertPaneUpload = document.getElementById("convert-pane-upload");
  const convertPaneEditor = document.getElementById("convert-pane-editor");
  const convertDropzone = document.getElementById("convert-dropzone");
  const convertFile = document.getElementById("convert-file");
  const reverseFile = document.getElementById("reverse-file");
  const reverseDropzone = document.getElementById("reverse-dropzone");
  const reverseFileName = document.getElementById("reverse-file-name");
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
  const diffDropA = document.getElementById("diff-drop-a");
  const diffDropB = document.getElementById("diff-drop-b");
  const diffFileAName = document.getElementById("diff-file-a-name");
  const diffFileBName = document.getElementById("diff-file-b-name");
  const diffOptionsPanel = document.getElementById("diff-options-panel");
  const toggleDiffOptions = document.getElementById("toggle-diff-options");
  const batchDropzone = document.getElementById("batch-dropzone");
  const batchFilesInput = document.getElementById("batch-files");
  const batchFileList = document.getElementById("batch-file-list");
  const batchOut = document.getElementById("batch-out");
  const batchClear = document.getElementById("batch-clear");
  const runBatch = document.getElementById("run-batch");
  const batchDryRun = document.getElementById("batch-dry-run");
  const copyCliBatch = document.getElementById("copy-cli-batch");
  const batchOptionsPanel = document.getElementById("batch-options-panel");
  const toggleBatchOptions = document.getElementById("toggle-batch-options");
  const batchExclude = document.getElementById("batch-exclude");
  const batchSkipExisting = document.getElementById("batch-skip-existing");
  const batchToc = document.getElementById("batch-toc");
  const batchNumbering = document.getElementById("batch-numbering");
  const batchPageNumbers = document.getElementById("batch-page-numbers");
  const batchNormalize = document.getElementById("batch-normalize");
  const batchTemplate = document.getElementById("batch-template");
  const batchTemplateFile = document.getElementById("batch-template-file");

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
  let convertInputMode = "upload";
  let diffInputMode = "upload";
  let optionsOpen = false;
  let batchOptionsOpen = false;
  let diffOptionsOpen = false;
  let batchItems = []; // { file, name, kind: 'md'|'zip' }
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

  function setConvertInputMode(mode) {
    convertInputMode = mode;
    document.querySelectorAll("#convert-input-mode .segmented__btn").forEach(function (btn) {
      btn.classList.toggle(
        "segmented__btn--active",
        btn.getAttribute("data-input-mode") === mode
      );
    });
    const isUpload = mode === "upload";
    convertPaneUpload.classList.toggle("hidden", !isUpload);
    convertPaneEditor.classList.toggle("hidden", isUpload);
    if (!isUpload) schedulePreview();
  }

  function setDiffInputMode(mode) {
    diffInputMode = mode;
    document.querySelectorAll("#diff-input-mode .segmented__btn").forEach(function (btn) {
      btn.classList.toggle(
        "segmented__btn--active",
        btn.getAttribute("data-diff-mode") === mode
      );
    });
    const isUpload = mode === "upload";
    diffDropA.classList.toggle("hidden", !isUpload);
    diffDropB.classList.toggle("hidden", !isUpload);
    diffA.classList.toggle("hidden", isUpload);
    diffB.classList.toggle("hidden", isUpload);
  }

  function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll(".mode-nav__btn").forEach(function (btn) {
      btn.classList.toggle("mode-nav__btn--active", btn.getAttribute("data-mode") === mode);
    });
    document.querySelectorAll("[data-mode-panel]").forEach(function (el) {
      const on = el.getAttribute("data-mode-panel") === mode;
      el.classList.toggle("hidden", !on);
      if (el.hasAttribute("hidden") || el.tagName === "MAIN" || el.classList.contains("workspace")) {
        el.hidden = !on;
      }
    });
    document.querySelector(".skip-link").setAttribute("href", "#workspace-" + mode);
    showError(null);

    if (mode === "convert") {
      if (!optionsOpen) optionsPanel.classList.add("hidden");
      if (!validateList.children.length) validatePanel.classList.add("hidden");
      setConvertInputMode(convertInputMode);
      if (convertInputMode === "paste") schedulePreview();
    }
    if (mode === "batch") {
      if (!batchOptionsOpen) batchOptionsPanel.classList.add("hidden");
      if (!batchOut.textContent.trim()) batchOut.textContent = t("batchEmpty");
    }
    if (mode === "diff") {
      if (!diffOptionsOpen) diffOptionsPanel.classList.add("hidden");
      setDiffInputMode(diffInputMode);
      if (!diffOut.textContent.trim()) diffOut.textContent = t("diffEmpty");
    }
  }

  function setText(id, key) {
    const el = document.getElementById(id);
    if (el) el.textContent = t(key);
  }

  function applyI18n() {
    document.title = t("pageTitle");
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";

    setText("i18n-header-hint", "headerHint");
    document.getElementById("lang-switch").setAttribute("aria-label", t("langLabel"));
    setText("mode-convert", "modeConvert");
    setText("mode-batch", "modeBatch");
    setText("mode-reverse", "modeReverse");
    setText("mode-diff", "modeDiff");
    setText("input-mode-upload", "inputUpload");
    setText("input-mode-paste", "inputPaste");
    setText("diff-mode-upload", "inputUpload");
    setText("diff-mode-paste", "inputPaste");
    setText("i18n-label-example", "labelExample");
    setText("i18n-label-preset", "labelPreset");
    setText("i18n-label-batch-preset", "labelPreset");
    setText("i18n-label-toc", "labelToc");
    setText("i18n-label-numbering", "labelNumbering");
    setText("i18n-label-title", "labelTitle");
    setText("i18n-label-author", "labelAuthor");
    setText("i18n-label-date", "labelDate");
    setText("i18n-label-version", "labelVersion");
    setText("i18n-label-toc-title", "labelTocTitle");
    setText("i18n-label-figure", "labelFigure");
    setText("i18n-label-table", "labelTable");
    setText("i18n-label-section", "labelSection");
    setText("i18n-label-normalize", "labelNormalize");
    setText("i18n-label-no-plugins", "labelNoPlugins");
    setText("i18n-label-strict-mermaid", "labelStrictMermaid");
    setText("i18n-label-validate-strict", "labelValidateStrict");
    setText("i18n-label-template", "labelTemplate");
    setText("i18n-label-template-upload", "labelTemplateUpload");
    setText("i18n-template-none", "templateNone");
    setText("i18n-batch-template-none", "templateNone");
    setText("i18n-label-page-numbers", "labelPageNumbers");
    setText("i18n-opt-doc", "optDoc");
    setText("i18n-opt-structure", "optStructure");
    setText("i18n-opt-captions", "optCaptions");
    setText("i18n-opt-behavior", "optBehavior");
    setText("i18n-opt-template", "optTemplate");
    setText("i18n-snippets-label", "snippetsLabel");
    setText("i18n-example-placeholder", "examplePlaceholder");
    setText("i18n-pane-upload", "paneUpload");
    setText("i18n-pane-markdown", "paneMarkdown");
    setText("i18n-pane-preview", "panePreview");
    setText("i18n-badge-approx", "badgeApproximation");
    setText("i18n-footer-privacy", "footerPrivacy");
    setText("i18n-label-diff-format", "labelDiffFormat");
    setText("i18n-pane-reverse-in", "paneReverseIn");
    setText("i18n-pane-reverse-out", "paneReverseOut");
    setText("i18n-pane-diff-a", "paneDiffA");
    setText("i18n-pane-diff-b", "paneDiffB");
    setText("i18n-pane-diff-out", "paneDiffOut");
    setText("i18n-pane-batch-in", "paneBatchIn");
    setText("i18n-pane-batch-out", "paneBatchOut");
    setText("i18n-convert-drop-title", "convertDropTitle");
    setText("i18n-convert-drop-hint", "convertDropHint");
    setText("i18n-batch-drop-title", "batchDropTitle");
    setText("i18n-batch-drop-hint", "batchDropHint");
    setText("i18n-reverse-drop-title", "reverseDropTitle");
    setText("i18n-reverse-empty", "reverseEmpty");
    setText("i18n-diff-drop-a", "diffDropA");
    setText("i18n-diff-drop-b", "diffDropB");
    setText("i18n-validate-title", "validateTitle");
    setText("i18n-label-exclude", "labelExclude");
    setText("i18n-label-skip-existing", "labelSkipExisting");
    setText("i18n-batch-opt-rules", "batchOptRules");
    setText("i18n-batch-opt-style", "batchOptStyle");
    setText("i18n-label-batch-toc", "labelToc");
    setText("i18n-label-batch-numbering", "labelNumbering");
    setText("i18n-label-batch-page-numbers", "labelPageNumbers");
    setText("i18n-label-batch-normalize", "labelNormalize");
    setText("i18n-label-batch-template", "labelTemplate");
    setText("i18n-label-batch-template-upload", "labelTemplateUpload");

    markdownEl.placeholder = t("placeholderMarkdown");
    reverseOut.placeholder = t("placeholderReverse");
    diffA.placeholder = t("diffEmpty");
    diffB.placeholder = t("diffEmpty");
    if (!diffOut.textContent.trim() || diffOut.dataset.empty === "1") {
      diffOut.textContent = t("diffEmpty");
      diffOut.dataset.empty = "1";
    }
    if (!batchOut.textContent.trim() || batchOut.dataset.empty === "1") {
      batchOut.textContent = t("batchEmpty");
      batchOut.dataset.empty = "1";
    }

    toggleOptions.textContent = optionsOpen ? t("btnOptionsHide") : t("btnOptions");
    toggleBatchOptions.textContent = batchOptionsOpen ? t("btnOptionsHide") : t("btnOptions");
    toggleDiffOptions.textContent = diffOptionsOpen ? t("btnOptionsHide") : t("btnOptions");
    copyCliBtn.textContent = t("btnCopyCli");
    copyCliReverse.textContent = t("btnCopyCli");
    copyCliDiff.textContent = t("btnCopyCli");
    copyCliBatch.textContent = t("btnCopyCli");
    sendToConvert.textContent = t("btnSendConvert");
    copyReverseMd.textContent = t("btnCopy");
    loadDiffSample.textContent = t("btnLoadSample");
    batchClear.textContent = t("btnClear");

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
    if (!runBatch.classList.contains("btn--loading")) {
      runBatch.querySelector(".btn__label").textContent = t("btnBatch");
    }
    if (!batchDryRun.classList.contains("btn--loading")) {
      batchDryRun.querySelector(".btn__label").textContent = t("btnDryRun");
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
    if (batchPresetEl.value) applyBatchPresetUi(batchPresetEl.value, false);
    if (currentMode === "convert" && convertInputMode === "paste") schedulePreview();
  }

  function setLang(lang) {
    currentLang = lang;
    localStorage.setItem("md-to-docx-lang", lang);
    applyI18n();
  }

  function fillPresetSelect(selectEl, selected) {
    selectEl.innerHTML = "";
    presetsCache.forEach(function (p) {
      const opt = document.createElement("option");
      opt.value = p.name;
      opt.textContent = p.name + " — " + presetDescription(p.name);
      selectEl.appendChild(opt);
    });
    if (selected && presetsCache.some(function (p) { return p.name === selected; })) {
      selectEl.value = selected;
    }
  }

  function rebuildPresetOptions() {
    fillPresetSelect(presetEl, presetEl.value || "technical");
    fillPresetSelect(batchPresetEl, batchPresetEl.value || "technical");
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

  function applyBatchPresetUi(name, syncChecks) {
    const preset = getPresetByName(name);
    if (!preset) return;
    if (syncChecks !== false) {
      batchToc.checked = preset.toc;
      batchNumbering.checked = preset.numbering;
    }
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

  function optionalField(el) {
    const v = el.value.trim();
    return v || null;
  }

  function convertFields() {
    return {
      preset: presetEl.value,
      toc: tocEl.checked,
      numbering: numberingEl.checked,
      page_numbers: pageNumbersEl.checked,
      title: optionalField(titleEl),
      author: optionalField(authorEl),
      date: optionalField(dateEl),
      doc_version: optionalField(versionEl),
      toc_title: optionalField(tocTitleEl),
      figure_label: optionalField(figureLabelEl),
      table_label: optionalField(tableLabelEl),
      section_label: optionalField(sectionLabelEl),
      normalize: normalizeEl.checked,
      no_plugins: noPluginsEl.checked,
      strict_mermaid: strictMermaidEl.checked,
      template: templateFileEl.files && templateFileEl.files[0] ? null : templateEl.value || null,
    };
  }

  function appendConvertFields(fd, fields) {
    fd.append("preset", fields.preset);
    fd.append("toc", String(fields.toc));
    fd.append("numbering", String(fields.numbering));
    fd.append("page_numbers", String(fields.page_numbers));
    fd.append("normalize", String(fields.normalize));
    fd.append("no_plugins", String(fields.no_plugins));
    fd.append("strict_mermaid", String(fields.strict_mermaid));
    ["title", "author", "date", "doc_version", "toc_title", "figure_label", "table_label", "section_label"].forEach(
      function (k) {
        if (fields[k]) fd.append(k, fields[k]);
      }
    );
    if (fields.template) fd.append("template", fields.template);
  }

  function convertCli() {
    const fields = convertFields();
    const parts = ["./bin/convert report.md --preset " + fields.preset];
    parts.push(fields.toc ? "--toc" : "--no-toc");
    if (fields.numbering) parts.push("--numbering");
    if (!fields.page_numbers) parts.push("--no-page-numbers");
    if (fields.toc_title) parts.push("--toc-title " + JSON.stringify(fields.toc_title));
    if (fields.title) parts.push("--title " + JSON.stringify(fields.title));
    if (fields.author) parts.push("--author " + JSON.stringify(fields.author));
    if (fields.date) parts.push("--date " + JSON.stringify(fields.date));
    if (fields.doc_version) parts.push("--doc-version " + JSON.stringify(fields.doc_version));
    if (fields.figure_label) parts.push("--figure-label " + JSON.stringify(fields.figure_label));
    if (fields.table_label) parts.push("--table-label " + JSON.stringify(fields.table_label));
    if (fields.section_label) parts.push("--section-label " + JSON.stringify(fields.section_label));
    if (!fields.normalize) parts.push("--no-normalize");
    if (fields.no_plugins) parts.push("--no-plugins");
    if (fields.strict_mermaid) parts.push("--strict-mermaid");
    if (templateFileEl.files && templateFileEl.files[0]) {
      parts.push("--template " + templateFileEl.files[0].name);
    } else if (fields.template) {
      parts.push("--template templates/" + fields.template + "/template.docx");
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
    batchPresetEl.value = "technical";
    applyPresetUi("technical");
    applyBatchPresetUi("technical");
  }

  async function loadTemplates() {
    try {
      const res = await fetch("/api/templates");
      const data = await res.json();
      (data.templates || []).forEach(function (tpl) {
        [templateEl, batchTemplate].forEach(function (sel) {
          const opt = document.createElement("option");
          opt.value = tpl.id;
          opt.textContent = tpl.name;
          sel.appendChild(opt);
        });
      });
    } catch (_) {
      /* optional */
    }
  }

  async function loadExample(name) {
    if (!name) return;
    showError(null);
    try {
      const res = await fetch("/examples/" + name + ".md");
      if (!res.ok) throw new Error("failed to load example");
      markdownEl.value = await res.text();
      setConvertInputMode("paste");
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

  async function ingestMdFile(file) {
    if (!file) return;
    const name = (file.name || "").toLowerCase();
    if (!name.endsWith(".md")) {
      showError({
        problem: t("errorNoMd"),
        cause: "expected .md",
        fix: t("errorNoMdFix"),
      });
      return;
    }
    markdownEl.value = await file.text();
    setConvertInputMode("paste");
    schedulePreview();
    showToast(t("toastMdLoaded", { name: file.name }));
  }

  async function generateDocx() {
    showError(null);
    if (!markdownEl.value.trim()) {
      showError({ problem: t("errorNoMd"), cause: "empty", fix: t("errorNoMdFix") });
      return;
    }
    setBtnLoading(generateBtn, true, "btnExport", "btnExportLoading");
    try {
      const fields = convertFields();
      let res;
      if (templateFileEl.files && templateFileEl.files[0]) {
        const fd = new FormData();
        fd.append("markdown", markdownEl.value);
        appendConvertFields(fd, fields);
        fd.append("template_file", templateFileEl.files[0], templateFileEl.files[0].name);
        res = await fetch("/api/convert", { method: "POST", body: fd });
      } else {
        const payload = { markdown: markdownEl.value, ...fields };
        Object.keys(payload).forEach(function (k) {
          if (payload[k] === null || payload[k] === undefined || payload[k] === "") delete payload[k];
        });
        res = await fetch("/api/convert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
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
        body: JSON.stringify({
          markdown: markdownEl.value,
          strict: validateStrictEl.checked,
          format: "json",
        }),
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
              setConvertInputMode("paste");
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
    setConvertInputMode("paste");
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

  function wireDropzone(zone, input, onFiles) {
    zone.addEventListener("click", function (e) {
      if (e.target === input) return;
      input.click();
    });
    zone.addEventListener("dragover", function (e) {
      e.preventDefault();
      zone.classList.add("dropzone--drag");
    });
    zone.addEventListener("dragleave", function () {
      zone.classList.remove("dropzone--drag");
    });
    zone.addEventListener("drop", function (e) {
      e.preventDefault();
      zone.classList.remove("dropzone--drag");
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) {
        onFiles(e.dataTransfer.files);
      }
    });
    input.addEventListener("change", function () {
      if (input.files && input.files.length) onFiles(input.files);
    });
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
      if (diffInputMode === "upload") {
        if (!fileA || !fileB) {
          showError({ problem: t("errorDiffEmpty"), cause: "missing uploads", fix: t("errorDiffEmptyFix") });
          return;
        }
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
      diffOut.dataset.empty = "0";
      showToast(t("toastDiffed"));
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(runDiff, false, "btnDiff", "btnDiffLoading");
    }
  }

  function renderBatchList() {
    batchFileList.innerHTML = "";
    if (!batchItems.length) {
      batchFileList.classList.add("hidden");
      batchDropzone.classList.remove("hidden");
      batchClear.hidden = true;
      return;
    }
    batchFileList.classList.remove("hidden");
    batchDropzone.classList.add("hidden");
    batchClear.hidden = false;
    batchItems.forEach(function (item, idx) {
      const li = document.createElement("li");
      li.className = "file-list__item";
      const name = document.createElement("span");
      name.textContent = item.name + " (" + formatBytes(item.file.size) + ")";
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "btn btn--ghost btn--small";
      remove.textContent = "×";
      remove.addEventListener("click", function () {
        batchItems.splice(idx, 1);
        renderBatchList();
      });
      li.appendChild(name);
      li.appendChild(remove);
      batchFileList.appendChild(li);
    });
  }

  function addBatchFiles(fileList) {
    const files = Array.from(fileList || []);
    if (!files.length) return;
    const zips = files.filter(function (f) {
      return (f.name || "").toLowerCase().endsWith(".zip");
    });
    const mds = files.filter(function (f) {
      return (f.name || "").toLowerCase().endsWith(".md");
    });
    if (zips.length && mds.length) {
      showError({
        problem: "Mixed upload",
        cause: "zip and markdown together",
        fix: "Upload either a zip or .md files",
      });
      return;
    }
    if (zips.length > 1) {
      showError({
        problem: "Too many zips",
        cause: "only one zip allowed",
        fix: "Drop a single zip archive",
      });
      return;
    }
    if (zips.length === 1) {
      batchItems = [{ file: zips[0], name: zips[0].name, kind: "zip" }];
    } else {
      batchItems = batchItems.filter(function (i) { return i.kind !== "zip"; });
      mds.forEach(function (f) {
        if (!batchItems.some(function (i) { return i.name === f.name && i.file.size === f.size; })) {
          batchItems.push({ file: f, name: f.name, kind: "md" });
        }
      });
    }
    renderBatchList();
    showError(null);
  }

  function batchCli() {
    const parts = ["md-to-docx ./docs --preset " + batchPresetEl.value];
    parts.push(batchToc.checked ? "--toc" : "--no-toc");
    if (batchNumbering.checked) parts.push("--numbering");
    if (!batchPageNumbers.checked) parts.push("--no-page-numbers");
    if (!batchNormalize.checked) parts.push("--no-normalize");
    if (batchSkipExisting.checked) parts.push("--skip-existing");
    batchExclude.value.split("\n").forEach(function (line) {
      const p = line.trim();
      if (p && !p.startsWith("#")) parts.push("--exclude " + JSON.stringify(p));
    });
    if (batchTemplate.value) {
      parts.push("--template templates/" + batchTemplate.value + "/template.docx");
    }
    return parts.join(" ");
  }

  async function runBatchConvert(dryRun) {
    showError(null);
    if (!batchItems.length) {
      showError({ problem: t("errorBatchEmpty"), cause: "empty", fix: t("errorBatchEmptyFix") });
      return;
    }
    const btn = dryRun ? batchDryRun : runBatch;
    const idle = dryRun ? "btnDryRun" : "btnBatch";
    const loading = dryRun ? "btnDryRunLoading" : "btnBatchLoading";
    setBtnLoading(btn, true, idle, loading);
    try {
      const fd = new FormData();
      const first = batchItems[0];
      if (first.kind === "zip") {
        fd.append("archive", first.file, first.name);
      } else {
        batchItems.forEach(function (item) {
          fd.append("files", item.file, item.name);
        });
      }
      fd.append("preset", batchPresetEl.value);
      fd.append("toc", String(batchToc.checked));
      fd.append("numbering", String(batchNumbering.checked));
      fd.append("page_numbers", String(batchPageNumbers.checked));
      fd.append("normalize", String(batchNormalize.checked));
      fd.append("dry_run", String(!!dryRun));
      fd.append("skip_existing", String(batchSkipExisting.checked));
      if (batchExclude.value.trim()) fd.append("exclude", batchExclude.value);
      if (batchTemplateFile.files && batchTemplateFile.files[0]) {
        fd.append("template_file", batchTemplateFile.files[0], batchTemplateFile.files[0].name);
      } else if (batchTemplate.value) {
        fd.append("template", batchTemplate.value);
      }
      const res = await fetch("/api/convert/batch", { method: "POST", body: fd });
      if (!res.ok) {
        let json = {};
        try { json = await res.json(); } catch (_) {}
        showError(parseError(res, json));
        return;
      }
      const ctype = res.headers.get("content-type") || "";
      if (ctype.indexOf("application/json") >= 0 || dryRun) {
        const data = await res.json();
        const lines = [];
        (data.planned || []).forEach(function (p) { lines.push("→ " + p); });
        (data.skipped || []).forEach(function (p) { lines.push("skip " + p); });
        batchOut.textContent = lines.join("\n") || t("batchEmpty");
        batchOut.dataset.empty = "0";
        showToast(t("toastBatchPlanned", { n: String((data.planned || []).length) }));
      } else {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "documents.zip";
        a.click();
        URL.revokeObjectURL(url);
        batchOut.textContent = "ZIP ready · " + (res.headers.get("X-Batch-Count") || "") + " file(s)";
        batchOut.dataset.empty = "0";
        showToast(t("toastBatchDownloaded"));
      }
    } catch (e) {
      showError({ problem: t("errorNetwork"), cause: String(e), fix: t("errorNetworkFix") });
    } finally {
      setBtnLoading(btn, false, idle, loading);
    }
  }

  function copyText(text) {
    navigator.clipboard.writeText(text).then(function () {
      showToast(t("toastCopied"));
    }).catch(function () {
      showError({ problem: t("errorCopy"), cause: "Clipboard access denied", fix: t("errorCopyFix") });
    });
  }

  /* ── events ── */
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
  batchPresetEl.addEventListener("change", function () {
    applyBatchPresetUi(batchPresetEl.value);
  });

  templateFileEl.addEventListener("change", function () {
    if (templateFileEl.files && templateFileEl.files[0]) templateEl.value = "";
  });
  templateEl.addEventListener("change", function () {
    if (templateEl.value) templateFileEl.value = "";
  });
  batchTemplateFile.addEventListener("change", function () {
    if (batchTemplateFile.files && batchTemplateFile.files[0]) batchTemplate.value = "";
  });
  batchTemplate.addEventListener("change", function () {
    if (batchTemplate.value) batchTemplateFile.value = "";
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
  toggleBatchOptions.addEventListener("click", function () {
    batchOptionsOpen = !batchOptionsOpen;
    batchOptionsPanel.classList.toggle("hidden", !batchOptionsOpen);
    toggleBatchOptions.setAttribute("aria-expanded", batchOptionsOpen ? "true" : "false");
    toggleBatchOptions.textContent = batchOptionsOpen ? t("btnOptionsHide") : t("btnOptions");
  });
  toggleDiffOptions.addEventListener("click", function () {
    diffOptionsOpen = !diffOptionsOpen;
    diffOptionsPanel.classList.toggle("hidden", !diffOptionsOpen);
    toggleDiffOptions.setAttribute("aria-expanded", diffOptionsOpen ? "true" : "false");
    toggleDiffOptions.textContent = diffOptionsOpen ? t("btnOptionsHide") : t("btnOptions");
  });

  document.querySelectorAll("#convert-input-mode .segmented__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setConvertInputMode(btn.getAttribute("data-input-mode"));
    });
  });
  document.querySelectorAll("#diff-input-mode .segmented__btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setDiffInputMode(btn.getAttribute("data-diff-mode"));
    });
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

  wireDropzone(convertDropzone, convertFile, function (files) {
    ingestMdFile(files[0]);
  });
  wireDropzone(reverseDropzone, reverseFile, function (files) {
    const dt = new DataTransfer();
    dt.items.add(files[0]);
    reverseFile.files = dt.files;
    reverseFileName.hidden = false;
    reverseFileName.textContent = files[0].name;
    doReverse();
  });
  wireDropzone(batchDropzone, batchFilesInput, addBatchFiles);
  wireDropzone(diffDropA, diffFileA, function (files) {
    const dt = new DataTransfer();
    dt.items.add(files[0]);
    diffFileA.files = dt.files;
    diffFileAName.hidden = false;
    diffFileAName.textContent = files[0].name;
    if (files[0].name.toLowerCase().endsWith(".md")) {
      files[0].text().then(function (text) { diffA.value = text; });
    }
  });
  wireDropzone(diffDropB, diffFileB, function (files) {
    const dt = new DataTransfer();
    dt.items.add(files[0]);
    diffFileB.files = dt.files;
    diffFileBName.hidden = false;
    diffFileBName.textContent = files[0].name;
    if (files[0].name.toLowerCase().endsWith(".md")) {
      files[0].text().then(function (text) { diffB.value = text; });
    }
  });

  batchClear.addEventListener("click", function () {
    batchItems = [];
    batchFilesInput.value = "";
    renderBatchList();
    batchOut.textContent = t("batchEmpty");
    batchOut.dataset.empty = "1";
  });
  runBatch.addEventListener("click", function () { runBatchConvert(false); });
  batchDryRun.addEventListener("click", function () { runBatchConvert(true); });
  copyCliBatch.addEventListener("click", function () { copyText(batchCli()); });

  copyCliBtn.addEventListener("click", function () { copyText(convertCli()); });
  copyCliReverse.addEventListener("click", function () {
    copyText("md-to-docx reverse input.docx -o report.md");
  });
  copyCliDiff.addEventListener("click", function () {
    copyText("md-to-docx diff a.md b.md --format " + diffFormat.value);
  });

  runReverse.addEventListener("click", doReverse);
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
    setConvertInputMode("paste");
    schedulePreview();
    showToast(t("toastSentConvert"));
  });

  runDiff.addEventListener("click", doDiff);
  loadDiffSample.addEventListener("click", function () {
    setDiffInputMode("paste");
    diffA.value = DIFF_SAMPLE_A;
    diffB.value = DIFF_SAMPLE_B;
    diffFileA.value = "";
    diffFileB.value = "";
    diffFileAName.hidden = true;
    diffFileBName.hidden = true;
    showToast(t("toastSample"));
    doDiff();
  });

  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (currentMode === "convert" && !generateBtn.disabled) generateDocx();
      if (currentMode === "batch" && !runBatch.disabled) runBatchConvert(false);
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
    setConvertInputMode("upload");
    updateCharCount();
  });
})();
