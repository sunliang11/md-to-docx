const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { JSDOM } = require("jsdom");

const ROOT = path.join(__dirname, "..");

function createDom(html, url = "https://example.com") {
  const dom = new JSDOM(html, {
    url,
    pretendToBeVisual: true,
    runScripts: "outside-only",
  });
  dom.window.MutationObserver = class {
    observe() {}
    disconnect() {}
  };
  return dom;
}

function runInWindow(dom, relPath) {
  const code = fs.readFileSync(path.join(ROOT, relPath), "utf8");
  vm.runInContext(code, dom.getInternalVMContext());
}

function loadFixture(name) {
  const html = fs.readFileSync(path.join(ROOT, "testdata", name), "utf8");
  return createDom(html);
}

function runAdapter(dom, adapterFile) {
  runInWindow(dom, "src/lib/html-to-md.js");
  runInWindow(dom, "src/lib/extract.js");
  dom.window.module = { exports: {} };
  runInWindow(dom, "src/content/" + adapterFile);
  return dom.window.module.exports;
}

test("htmlToMarkdown preserves headings and code", () => {
  const dom = createDom("<body><h1>Title</h1></body>");
  runInWindow(dom, "src/lib/html-to-md.js");
  const md = dom.window.MdToDocxHtml.htmlToMarkdown(
    "<h2>Hi</h2><pre><code class=\"language-js\">x</code></pre>"
  );
  assert.match(md, /## Hi/);
  assert.match(md, /```js/);
});

test("chatgpt adapter extracts latest assistant", () => {
  const dom = loadFixture("chatgpt-sample.html");
  const exports = runAdapter(dom, "chatgpt.js");
  const data = exports.extractLatestAssistantMarkdown(dom.window.document);
  assert.ok(data);
  assert.match(data.markdown, /Sample Report/);
  assert.match(data.markdown, /test/);
});

test("claude adapter extracts message", () => {
  const dom = loadFixture("claude-sample.html");
  const exports = runAdapter(dom, "claude.js");
  const data = exports.extractLatestAssistantMarkdown(dom.window.document);
  assert.ok(data);
  assert.match(data.markdown, /Design Doc/);
  assert.match(data.markdown, /Item one/);
});

test("htmlToMarkdown strips script content from flow", () => {
  const dom = createDom("<body></body>");
  runInWindow(dom, "src/lib/html-to-md.js");
  const md = dom.window.MdToDocxHtml.htmlToMarkdown(
    "<p>Hello</p><script>alert(1)</script>"
  );
  assert.match(md, /Hello/);
});
