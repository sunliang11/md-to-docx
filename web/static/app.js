(function () {
  const markdownEl = document.getElementById("markdown");
  const previewEl = document.getElementById("preview");
  const presetEl = document.getElementById("preset");
  const tocEl = document.getElementById("toc");
  const exampleEl = document.getElementById("example");
  const generateBtn = document.getElementById("generate");
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

  const md = window.markdownit({ html: false, linkify: true, breaks: true });

  let debounceTimer;
  let toastTimer;
  let presetsCache = [];
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

  function applyI18n() {
    document.title = t("pageTitle");
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";

    document.getElementById("i18n-header-hint").textContent = t("headerHint");
    document.getElementById("lang-switch").setAttribute("aria-label", t("langLabel"));
    document.getElementById("i18n-label-example").textContent = t("labelExample");
    document.getElementById("i18n-label-preset").textContent = t("labelPreset");
    document.getElementById("i18n-label-toc").textContent = t("labelToc");
    document.getElementById("i18n-example-placeholder").textContent = t("examplePlaceholder");
    document.getElementById("i18n-pane-markdown").textContent = t("paneMarkdown");
    document.getElementById("i18n-pane-preview").textContent = t("panePreview");
    document.getElementById("i18n-badge-approx").textContent = t("badgeApproximation");
    document.getElementById("i18n-footer-privacy").textContent = t("footerPrivacy");
    markdownEl.placeholder = t("placeholderMarkdown");

    copyCliBtn.textContent = t("btnCopyCli");
    if (!generateBtn.classList.contains("btn--loading")) {
      document.querySelector("#generate .btn__label").textContent = t("btnExport");
    }
    errorDismiss.setAttribute("aria-label", t("errorDismiss"));

    langEnBtn.classList.toggle("lang-switch__btn--active", currentLang === "en");
    langZhBtn.classList.toggle("lang-switch__btn--active", currentLang === "zh");

    exampleEl.querySelectorAll("option[data-example-key]").forEach(function (opt) {
      const key = opt.getAttribute("data-example-key");
      opt.textContent = messages().exampleOptions[key] || key;
    });

    rebuildPresetOptions();
    if (lastErrorDetail) {
      showError(lastErrorDetail);
    }
    if (presetEl.value) {
      applyPresetUi(presetEl.value, false);
    }
    updatePreview();
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
    if (selected && presetsCache.some(function (p) {
      return p.name === selected;
    })) {
      presetEl.value = selected;
    }
  }

  function applyPresetUi(name, syncToc) {
    const preset = getPresetByName(name);
    if (!preset) return;

    if (syncToc !== false) {
      tocEl.checked = preset.toc;
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
      t("presetHintFonts", {
        latin: latin,
        east_asia: eastAsia,
        pt: String(bodyPt),
      }),
      preset.toc ? t("presetHintTocOn") : t("presetHintTocOff"),
      preset.numbering ? t("presetHintNumberingOn") : t("presetHintNumberingOff"),
    ];
    if (pv.header) {
      parts.push(t("presetHintHeader", { header: pv.header }));
    }
    presetHintEl.textContent = parts.join(" · ");
  }

  function applyHeadingNumbers() {
    const preset = getPresetByName(presetEl.value);
    if (!preset || !preset.numbering) return;

    const counters = [0, 0, 0];
    previewEl.querySelectorAll("h1, h2, h3").forEach(function (el) {
      const level = parseInt(el.tagName.charAt(1), 10);
      if (level < 1 || level > 3) return;
      counters[level - 1] += 1;
      for (let i = level; i < 3; i++) counters[i + 1] = 0;

      let num = "";
      if (level === 1) num = String(counters[0]);
      else if (level === 2) num = counters[0] + "." + counters[1];
      else num = counters[0] + "." + counters[1] + "." + counters[2];

      const span = document.createElement("span");
      span.className = "heading-num";
      span.textContent = num + ". ";
      el.insertBefore(span, el.firstChild);
    });
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

  function setLoading(loading) {
    generateBtn.disabled = loading;
    generateBtn.classList.toggle("btn--loading", loading);
    generateBtn.querySelector(".btn__label").textContent = loading
      ? t("btnExportLoading")
      : t("btnExport");
  }

  function updateCharCount() {
    const bytes = new TextEncoder().encode(markdownEl.value).length;
    charCountEl.textContent = formatBytes(bytes);
  }

  function updatePreview() {
    const text = markdownEl.value;
    updateCharCount();
    if (!text.trim()) {
      previewEl.innerHTML = "";
      previewEl.classList.add("preview--empty");
      previewEl.textContent = t("previewEmpty");
      return;
    }
    previewEl.classList.remove("preview--empty");
    previewEl.innerHTML = md.render(text);
    applyHeadingNumbers();
  }

  markdownEl.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updatePreview, 300);
  });

  errorDismiss.addEventListener("click", function () {
    showError(null);
  });

  presetEl.addEventListener("change", function () {
    applyPresetUi(presetEl.value);
    updatePreview();
  });

  langEnBtn.addEventListener("click", function () {
    setLang("en");
  });
  langZhBtn.addEventListener("click", function () {
    setLang("zh");
  });

  async function loadPresets() {
    const res = await fetch("/api/presets");
    const data = await res.json();
    presetsCache = data.presets;
    rebuildPresetOptions();
    presetEl.value = "technical";
    applyPresetUi("technical");
  }

  async function loadExample(name) {
    if (!name) return;
    showError(null);
    try {
      const res = await fetch("/examples/" + name + ".md");
      if (!res.ok) throw new Error("failed to load example");
      markdownEl.value = await res.text();
      updatePreview();
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

  exampleEl.addEventListener("change", function () {
    loadExample(exampleEl.value);
  });

  async function generateDocx() {
    showError(null);
    setLoading(true);
    const body = {
      markdown: markdownEl.value,
      preset: presetEl.value,
      toc: tocEl.checked,
    };
    try {
      const res = await fetch("/api/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        let detail = {};
        try {
          const json = await res.json();
          detail = json.detail || json;
        } catch (_) {
          detail = { problem: "Request failed", cause: res.statusText, fix: "Try again" };
        }
        showError(detail);
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
      showError({
        problem: t("errorNetwork"),
        cause: String(e),
        fix: t("errorNetworkFix"),
      });
    } finally {
      setLoading(false);
    }
  }

  generateBtn.addEventListener("click", generateDocx);

  copyCliBtn.addEventListener("click", function () {
    const preset = presetEl.value;
    const toc = tocEl.checked ? " --toc" : "";
    const cmd = "./bin/convert report.md --preset " + preset + toc;
    navigator.clipboard.writeText(cmd).then(function () {
      showToast(t("toastCopied"));
    }).catch(function () {
      showError({
        problem: t("errorCopy"),
        cause: "Clipboard access denied",
        fix: t("errorCopyFix"),
      });
    });
  });

  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (!generateBtn.disabled) generateDocx();
    }
  });

  loadPresets().then(function () {
    applyI18n();
    markdownEl.value = currentLang === "zh"
      ? "# 技术报告\n\n在此粘贴 AI 生成的 Markdown。\n"
      : "# Technical Report\n\nPaste AI-generated Markdown here.\n";
    updatePreview();
  });
})();
