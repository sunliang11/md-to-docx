(function (global) {
  const DEFAULTS = {
    endpoint: "http://127.0.0.1:8080",
    preset: "technical",
    fallbackMd: true,
    showFloating: true,
  };

  const LABEL_WORD = "Export to Word";
  const LABEL_MD = "Export MD";
  const PROBE_TTL_MS = 30000;
  const DRAG_THRESHOLD = 4;

  let probeCache = { at: 0, online: false, endpoint: "" };
  const trackedButtons = new Set();

  function showToast(message) {
    const existing = document.querySelector(".md-to-docx-toast");
    if (existing) existing.remove();
    const el = document.createElement("div");
    el.className = "md-to-docx-toast";
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 6000);
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }

  function downloadText(text, filename) {
    downloadBlob(new Blob([text], { type: "text/markdown" }), filename);
  }

  function isExtensionAlive() {
    try {
      return !!(typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.id);
    } catch (_) {
      return false;
    }
  }

  function isContextError(err) {
    const msg = String((err && err.message) || err || "");
    return /invalidated|extension context/i.test(msg);
  }

  function lastErrorIsContext() {
    try {
      const err = chrome.runtime && chrome.runtime.lastError;
      return err && isContextError(err);
    } catch (_) {
      return true;
    }
  }

  function removeStaleFloatUi() {
    try {
      document.querySelectorAll(".md-to-docx-float").forEach((el) => el.remove());
    } catch (_) {}
  }

  function handleDeadContext(toastMsg) {
    removeStaleFloatUi();
    showToast(toastMsg || "Extension was updated — refresh this page");
  }

  async function getSettings() {
    if (!isExtensionAlive()) {
      return { ...DEFAULTS };
    }
    return new Promise((resolve) => {
      try {
        chrome.storage.sync.get(DEFAULTS, (items) => {
          if (lastErrorIsContext()) {
            resolve({ ...DEFAULTS });
            return;
          }
          resolve({ ...DEFAULTS, ...(items || {}) });
        });
      } catch (err) {
        if (isContextError(err)) {
          resolve({ ...DEFAULTS });
          return;
        }
        resolve({ ...DEFAULTS });
      }
    });
  }

  function storageLocalGet(keys) {
    if (!isExtensionAlive()) return Promise.resolve({});
    return new Promise((resolve) => {
      try {
        chrome.storage.local.get(keys, (items) => {
          if (lastErrorIsContext()) {
            resolve({});
            return;
          }
          resolve(items || {});
        });
      } catch (_) {
        resolve({});
      }
    });
  }

  function storageLocalSet(obj) {
    if (!isExtensionAlive()) return Promise.resolve();
    return new Promise((resolve) => {
      try {
        chrome.storage.local.set(obj, () => {
          lastErrorIsContext();
          resolve();
        });
      } catch (_) {
        resolve();
      }
    });
  }

  function storageSyncSet(obj) {
    if (!isExtensionAlive()) return Promise.resolve();
    return new Promise((resolve) => {
      try {
        chrome.storage.sync.set(obj, () => {
          lastErrorIsContext();
          resolve();
        });
      } catch (_) {
        resolve();
      }
    });
  }

  function exportLabel(online) {
    return online ? LABEL_WORD : LABEL_MD;
  }

  function refreshTrackedLabels(online) {
    const label = exportLabel(online);
    trackedButtons.forEach((btn) => {
      if (btn && btn.isConnected) {
        btn.textContent = label;
        btn.dataset.mdToDocxMode = online ? "word" : "md";
      }
    });
  }

  async function probeEndpoint(force) {
    const settings = await getSettings();
    const endpoint = (settings.endpoint || DEFAULTS.endpoint).replace(/\/$/, "");
    const now = Date.now();
    if (
      !force &&
      probeCache.endpoint === endpoint &&
      now - probeCache.at < PROBE_TTL_MS
    ) {
      return probeCache.online;
    }

    let online = false;
    try {
      const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
      const timer = controller ? setTimeout(() => controller.abort(), 2500) : null;
      const res = await fetch(endpoint + "/healthz", {
        method: "GET",
        signal: controller ? controller.signal : undefined,
      });
      if (timer) clearTimeout(timer);
      online = res.ok;
    } catch (_) {
      online = false;
    }

    probeCache = { at: now, online, endpoint };
    refreshTrackedLabels(online);
    return online;
  }

  function trackButton(btn) {
    trackedButtons.add(btn);
    probeEndpoint(false)
      .then((online) => {
        if (!btn || !btn.isConnected) return;
        btn.textContent = exportLabel(online);
        btn.dataset.mdToDocxMode = online ? "word" : "md";
      })
      .catch(() => {});
  }

  async function convertAndDownload(markdown, title) {
    const safeTitle = global.MdToDocxExtract.sanitizeTitle(title);
    let settings = { ...DEFAULTS };
    let dead = !isExtensionAlive();

    try {
      settings = await getSettings();
    } catch (err) {
      if (isContextError(err)) dead = true;
    }

    if (dead || !isExtensionAlive()) {
      if (settings.fallbackMd !== false) {
        downloadText(markdown, safeTitle + ".md");
        handleDeadContext(
          "Downloaded " + safeTitle + ".md — extension was updated, refresh this page"
        );
      } else {
        handleDeadContext();
      }
      return;
    }

    const endpoint = settings.endpoint.replace(/\/$/, "");
    let online = false;
    try {
      online = await probeEndpoint(true);
    } catch (err) {
      if (isContextError(err)) {
        downloadText(markdown, safeTitle + ".md");
        handleDeadContext(
          "Downloaded " + safeTitle + ".md — extension was updated, refresh this page"
        );
        return;
      }
      online = false;
    }

    if (!online) {
      if (settings.fallbackMd) {
        downloadText(markdown, safeTitle + ".md");
        showToast("Downloaded " + safeTitle + ".md (Playground offline)");
      } else {
        showToast("Playground offline. Enable MD fallback in extension options.");
      }
      return;
    }

    try {
      const res = await fetch(endpoint + "/api/convert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          markdown,
          preset: settings.preset,
          toc: true,
        }),
      });

      if (!res.ok) {
        let detail = "Convert failed";
        try {
          const json = await res.json();
          detail = json.detail?.problem || json.detail?.cause || JSON.stringify(json.detail);
        } catch (_) {
          detail = res.statusText;
        }
        throw new Error(detail);
      }

      const blob = await res.blob();
      downloadBlob(blob, safeTitle + ".docx");
      showToast("Downloaded " + safeTitle + ".docx");
      refreshTrackedLabels(true);
    } catch (err) {
      if (isContextError(err)) {
        downloadText(markdown, safeTitle + ".md");
        handleDeadContext(
          "Downloaded " + safeTitle + ".md — extension was updated, refresh this page"
        );
        return;
      }
      probeCache = { at: Date.now(), online: false, endpoint };
      refreshTrackedLabels(false);
      if (settings.fallbackMd) {
        downloadText(markdown, safeTitle + ".md");
        showToast(
          "Downloaded " +
            safeTitle +
            ".md (Playground offline). Hint: docker compose -f web/docker-compose.yml up --build"
        );
      } else {
        showToast(err.message || "Export failed");
      }
    }
  }

  function injectExportButton(container, onClick) {
    if (!container || container.querySelector(".md-to-docx-export-btn")) return null;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "md-to-docx-export-btn";
    btn.textContent = LABEL_WORD;
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      onClick();
    });
    container.appendChild(btn);
    trackButton(btn);
    return btn;
  }

  function clampFloatPosition(wrap, left, top) {
    const pad = 8;
    const w = wrap.offsetWidth || 140;
    const h = wrap.offsetHeight || 40;
    const maxL = Math.max(pad, window.innerWidth - w - pad);
    const maxT = Math.max(pad, window.innerHeight - h - pad);
    return {
      left: Math.min(Math.max(pad, left), maxL),
      top: Math.min(Math.max(pad, top), maxT),
    };
  }

  function applyFloatPosition(wrap, pos) {
    if (!pos || typeof pos.left !== "number" || typeof pos.top !== "number") {
      wrap.style.left = "";
      wrap.style.top = "";
      wrap.style.right = "20px";
      wrap.style.bottom = "20px";
      updateFloatPeekSide(wrap);
      return;
    }
    const clamped = clampFloatPosition(wrap, pos.left, pos.top);
    wrap.style.right = "auto";
    wrap.style.bottom = "auto";
    wrap.style.left = clamped.left + "px";
    wrap.style.top = clamped.top + "px";
    updateFloatPeekSide(wrap);
  }

  function updateFloatPeekSide(wrap) {
    const rect = wrap.getBoundingClientRect();
    const mid = rect.left + rect.width / 2;
    if (mid < window.innerWidth / 2) {
      wrap.classList.add("md-to-docx-float-peek-left");
      wrap.classList.remove("md-to-docx-float-peek-right");
    } else {
      wrap.classList.add("md-to-docx-float-peek-right");
      wrap.classList.remove("md-to-docx-float-peek-left");
    }
  }

  function setFloatCollapsed(wrap, collapsed) {
    wrap.classList.toggle("md-to-docx-float-collapsed", !!collapsed);
    updateFloatPeekSide(wrap);
    storageLocalSet({ floatCollapsed: !!collapsed }).catch(() => {});
  }

  function enableFloatDrag(wrap) {
    let dragging = false;
    let moved = false;
    let startX = 0;
    let startY = 0;
    let origL = 0;
    let origT = 0;

    wrap.addEventListener("pointerdown", (e) => {
      if (e.button !== 0) return;
      if (e.target.closest(".md-to-docx-float-close")) return;
      const rect = wrap.getBoundingClientRect();
      dragging = true;
      moved = false;
      startX = e.clientX;
      startY = e.clientY;
      origL = rect.left;
      origT = rect.top;
      wrap.classList.add("md-to-docx-float-dragging");
      try {
        wrap.setPointerCapture(e.pointerId);
      } catch (_) {}
    });

    wrap.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      if (!moved && Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
      moved = true;
      const next = clampFloatPosition(wrap, origL + dx, origT + dy);
      wrap.style.right = "auto";
      wrap.style.bottom = "auto";
      wrap.style.left = next.left + "px";
      wrap.style.top = next.top + "px";
    });

    function endDrag(e) {
      if (!dragging) return;
      dragging = false;
      wrap.classList.remove("md-to-docx-float-dragging");
      try {
        wrap.releasePointerCapture(e.pointerId);
      } catch (_) {}
      if (moved) {
        const rect = wrap.getBoundingClientRect();
        const pos = clampFloatPosition(wrap, rect.left, rect.top);
        applyFloatPosition(wrap, pos);
        storageLocalSet({ floatPos: pos }).catch(() => {});
        wrap.dataset.dragged = "1";
        setTimeout(() => {
          delete wrap.dataset.dragged;
        }, 0);
      }
    }

    wrap.addEventListener("pointerup", endDrag);
    wrap.addEventListener("pointercancel", endDrag);
  }

  function injectFloatingButton(onClick, options) {
    const opts = options || {};
    const existing = document.querySelector(".md-to-docx-float");
    if (existing) {
      const btn = existing.querySelector(".md-to-docx-float-export");
      if (btn && !trackedButtons.has(btn)) trackButton(btn);
      return btn || existing;
    }

    const wrap = document.createElement("div");
    wrap.className = "md-to-docx-float";
    wrap.style.display = "none";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "md-to-docx-export-btn md-to-docx-float-export";
    btn.textContent = LABEL_WORD;
    btn.title = "Export page or selection (drag to move)";

    const close = document.createElement("button");
    close.type = "button";
    close.className = "md-to-docx-float-close";
    close.setAttribute("aria-label", "Collapse floating button");
    close.title = "Collapse to edge";
    close.textContent = "×";

    wrap.appendChild(btn);
    wrap.appendChild(close);
    // Start collapsed until storage restore finishes
    wrap.classList.add("md-to-docx-float-collapsed", "md-to-docx-float-peek-right");

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (wrap.dataset.dragged === "1") return;
      onClick();
    });

    close.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      setFloatCollapsed(wrap, true);
      showToast("Collapsed to edge — hover to expand");
    });

    enableFloatDrag(wrap);

    function mount() {
      if (!document.body) return;
      if (document.querySelector(".md-to-docx-float")) return;
      document.body.appendChild(wrap);
      trackButton(btn);
      storageLocalGet(["floatPos", "floatCollapsed"])
        .then((items) => {
          applyFloatPosition(wrap, items.floatPos);
          // Default collapsed (edge peek); only expand by default if user set floatCollapsed: false
          const collapsed = items.floatCollapsed !== false;
          setFloatCollapsed(wrap, collapsed);
        })
        .catch(() => {
          setFloatCollapsed(wrap, true);
        });
    }

    getSettings()
      .then((settings) => {
        if (opts.requireSetting !== false && settings.showFloating === false) return;
        wrap.style.display = "";
        if (document.body) mount();
        else document.addEventListener("DOMContentLoaded", mount, { once: true });
      })
      .catch(() => {});

    return btn;
  }

  if (typeof document !== "undefined") {
    setTimeout(() => {
      probeEndpoint(false).catch(() => {});
    }, 0);
  }

  global.MdToDocxExport = {
    convertAndDownload,
    injectExportButton,
    injectFloatingButton,
    showToast,
    probeEndpoint,
    getSettings,
    isExtensionAlive,
    exportLabel,
    LABEL_WORD,
    LABEL_MD,
    DEFAULTS,
  };
})(typeof window !== "undefined" ? window : globalThis);
