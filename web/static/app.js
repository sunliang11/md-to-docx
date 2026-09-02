(function () {
  const markdownEl = document.getElementById("markdown");
  const previewEl = document.getElementById("preview");
  const presetEl = document.getElementById("preset");
  const tocEl = document.getElementById("toc");
  const generateBtn = document.getElementById("generate");
  const copyCliBtn = document.getElementById("copy-cli");
  const exampleEl = document.getElementById("example");
  const errorEl = document.getElementById("error");

  const md = window.markdownit({ html: false, linkify: true, breaks: true });

  let debounceTimer;

  function showError(detail) {
    if (!detail) {
      errorEl.classList.add("hidden");
      errorEl.textContent = "";
      return;
    }
    const parts = [];
    if (detail.problem) parts.push("Problem: " + detail.problem);
    if (detail.cause) parts.push("Cause: " + detail.cause);
    if (detail.fix) parts.push("Fix: " + detail.fix);
    errorEl.textContent = parts.join("\n");
    errorEl.classList.remove("hidden");
  }

  function updatePreview() {
    previewEl.innerHTML = md.render(markdownEl.value);
  }

  markdownEl.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(updatePreview, 300);
  });

  async function loadPresets() {
    const res = await fetch("/api/presets");
    const data = await res.json();
    presetEl.innerHTML = "";
    data.presets.forEach(function (p) {
      const opt = document.createElement("option");
      opt.value = p.name;
      opt.textContent = p.name + " — " + (p.description || "");
      presetEl.appendChild(opt);
    });
    presetEl.value = "technical";
  }

  exampleEl.addEventListener("change", async function () {
    const name = exampleEl.value;
    if (!name) return;
    try {
      const res = await fetch("/examples/" + name + ".md");
      if (!res.ok) throw new Error("failed to load example");
      markdownEl.value = await res.text();
      updatePreview();
    } catch (e) {
      showError({ problem: "Example load failed", cause: String(e), fix: "Try another example" });
    }
  });

  generateBtn.addEventListener("click", async function () {
    showError(null);
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
    } catch (e) {
      showError({ problem: "Network error", cause: String(e), fix: "Check server is running" });
    }
  });

  copyCliBtn.addEventListener("click", function () {
    const preset = presetEl.value;
    const toc = tocEl.checked ? " --toc" : "";
    const cmd = "./bin/convert report.md --preset " + preset + toc;
    navigator.clipboard.writeText(cmd).then(function () {
      copyCliBtn.textContent = "Copied!";
      setTimeout(function () { copyCliBtn.textContent = "Copy CLI command"; }, 1500);
    });
  });

  loadPresets();
  markdownEl.value = "# Technical Report\n\nPaste AI-generated Markdown here.\n";
  updatePreview();
})();
