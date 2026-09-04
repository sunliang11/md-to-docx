const DEFAULTS = {
  endpoint: "http://127.0.0.1:8080",
  preset: "technical",
  fallbackMd: true,
  showFloating: true,
};

document.getElementById("save").addEventListener("click", () => {
  const endpoint = document.getElementById("endpoint").value.trim().replace(/\/$/, "");
  const preset = document.getElementById("preset").value;
  const fallbackMd = document.getElementById("fallbackMd").checked;
  const showFloating = document.getElementById("showFloating").checked;
  chrome.storage.sync.set({ endpoint, preset, fallbackMd, showFloating }, () => {
    document.getElementById("status").textContent = "Saved. Refresh open tabs to apply.";
  });
});

chrome.storage.sync.get(DEFAULTS, (items) => {
  document.getElementById("endpoint").value = items.endpoint;
  document.getElementById("preset").value = items.preset;
  document.getElementById("fallbackMd").checked = items.fallbackMd !== false;
  document.getElementById("showFloating").checked = items.showFloating !== false;
});
