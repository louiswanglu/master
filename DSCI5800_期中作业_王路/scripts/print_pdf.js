// Print the report to PDF through the Chrome DevTools Protocol so that we can use a
// custom footer template (page numbers) while keeping the 1-inch margins.
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const [, , inputHtml, outputPdf] = process.argv;
const PORT = 9333;
const PROFILE = path.join(os.tmpdir(), "dsh-print-profile-" + Date.now());

const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-crash-reporter",
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`,
  "--no-first-run", "--no-default-browser-check", "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      const j = await r.json();
      if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
    } catch (e) { /* not up yet */ }
    await sleep(300);
  }
  throw new Error("chrome devtools not reachable");
}

(async () => {
  const wsUrl = await getWsUrl();
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  await new Promise((r) => (ws.onopen = r));
  const send = (method, params = {}, sessionId) =>
    new Promise((res) => {
      const mid = ++id;
      pending.set(mid, res);
      ws.send(JSON.stringify({ id: mid, method, params, sessionId }));
    });

  const { result: { targetId } } = await send("Target.createTarget", { url: "about:blank" });
  const { result: { sessionId } } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Page.navigate", { url: "file://" + path.resolve(inputHtml) }, sessionId);
  await sleep(3500);

  const footer = `<div style="width:100%;font-family:'Times New Roman',serif;font-size:9pt;
    color:#444;padding:0 0.28in;display:flex;justify-content:space-between;">
    <span style="font-size:8.5pt">DSCI5800 期中作业 · 王路</span>
    <span>第 <span class="pageNumber"></span> 页 / 共 <span class="totalPages"></span> 页</span></div>`;

  const { result } = await send("Page.printToPDF", {
    printBackground: true,
    paperWidth: 8.27, paperHeight: 11.69,
    marginTop: 1, marginBottom: 1, marginLeft: 1, marginRight: 1,
    displayHeaderFooter: true,
    headerTemplate: "<div></div>",
    footerTemplate: footer,
    preferCSSPageSize: false,
    scale: 1,
  }, sessionId);

  fs.writeFileSync(outputPdf, Buffer.from(result.data, "base64"));
  console.log("wrote", outputPdf, fs.statSync(outputPdf).size, "bytes");
  ws.close();
  chrome.kill();
  process.exit(0);
})().catch((e) => { console.error(e); chrome.kill(); process.exit(1); });
