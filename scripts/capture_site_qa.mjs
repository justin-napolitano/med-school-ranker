import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const baseUrl = process.env.SITE_QA_BASE_URL || "http://localhost:8766";
const outDir = process.env.SITE_QA_OUT_DIR || "outputs/site_qa/screenshots";
const label = process.argv[2] || process.env.SITE_QA_LABEL || "before";
const chromePath =
  process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const debugPort = Number(process.env.CHROME_DEBUG_PORT || "9225");

fs.mkdirSync(outDir, { recursive: true });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${options.method || "GET"} ${url} returned ${response.status}`);
  }
  return response.json();
}

async function waitForChrome() {
  const versionUrl = `http://127.0.0.1:${debugPort}/json/version`;
  for (let i = 0; i < 60; i += 1) {
    try {
      return await fetchJson(versionUrl);
    } catch {
      await sleep(250);
    }
  }
  throw new Error("Chrome did not expose the DevTools endpoint in time.");
}

function connect(wsUrl) {
  const socket = new WebSocket(wsUrl);
  let nextId = 1;
  const pending = new Map();
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) return;
    const { resolve, reject } = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) reject(new Error(JSON.stringify(message.error)));
    else resolve(message.result || {});
  });
  return new Promise((resolve, reject) => {
    socket.addEventListener("open", () => {
      resolve({
        send(method, params = {}) {
          const id = nextId;
          nextId += 1;
          socket.send(JSON.stringify({ id, method, params }));
          return new Promise((methodResolve, methodReject) => {
            pending.set(id, { resolve: methodResolve, reject: methodReject });
          });
        },
        close() {
          socket.close();
        },
      });
    });
    socket.addEventListener("error", reject);
  });
}

async function loadPage(cdp, route, viewport) {
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: viewport.deviceScaleFactor || 1,
    mobile: Boolean(viewport.mobile),
  });
  await cdp.send("Page.navigate", { url: `${baseUrl}${route}` });
  await sleep(1200);
  await cdp.send("Runtime.evaluate", {
    expression: "document.fonts && document.fonts.ready",
    awaitPromise: true,
  });
  await evalPage(
    cdp,
    `(() => {
      window.scrollTo(0, 0);
      document.querySelectorAll(".table-wrap").forEach(element => {
        element.scrollLeft = 0;
        element.scrollTop = 0;
      });
      return true;
    })();`,
  );
  await sleep(300);
}

async function evalPage(cdp, expression) {
  return cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
}

async function screenshot(cdp, filename) {
  const fullPage = process.env.SITE_QA_FULL_PAGE === "1";
  let image;
  if (fullPage) {
    const metrics = await cdp.send("Page.getLayoutMetrics");
    const width = Math.ceil(metrics.cssContentSize?.width || 1440);
    const height = Math.ceil(metrics.cssContentSize?.height || 1000);
    image = await cdp.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: true,
      fromSurface: true,
      clip: { x: 0, y: 0, width, height, scale: 1 },
    });
  } else {
    image = await cdp.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
      fromSurface: true,
    });
  }
  fs.writeFileSync(path.join(outDir, filename), Buffer.from(image.data, "base64"));
}

async function setSelectorValues(cdp) {
  await evalPage(
    cdp,
    `(() => {
      const setValue = (id, preferred) => {
        const element = document.getElementById(id);
        if (!element) return null;
        const values = [...element.options].map(option => option.value);
        const value = values.includes(preferred) ? preferred : values.find(Boolean) || "";
        element.value = value;
        element.dispatchEvent(new Event("change", { bubbles: true }));
        return value;
      };
      return {
        mcat: setValue("selectorMcatBand", "506-509"),
        gpa: setValue("selectorGpaBand", "Greater than 3.79"),
        state: setValue("selectorApplicantState", "FL"),
      };
    })();`,
  );
  await sleep(600);
}

async function firstMdProfileRoute(cdp) {
  const result = await evalPage(
    cdp,
    `(() => {
      const md = rows("schools").find(item => item.school.degree_type === "MD" && item.profile_route);
      return md ? md.profile_route : "#/rankings";
    })();`,
  );
  return result.result?.value || "#/rankings";
}

async function scrollToWhyThisRank(cdp) {
  await evalPage(
    cdp,
    `(() => {
      const heading = [...document.querySelectorAll("h3")].find(item => item.textContent.trim() === "Why This Rank?");
      if (heading) heading.scrollIntoView({ block: "start" });
      return Boolean(heading);
    })();`,
  );
  await sleep(400);
}

async function main() {
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "med-school-site-qa-"));
  const chrome = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ]);
  chrome.stderr.on("data", () => {});
  chrome.stdout.on("data", () => {});

  try {
    await waitForChrome();
    const targets = await fetchJson(`http://127.0.0.1:${debugPort}/json/list`);
    const pageTarget = targets.find((target) => target.type === "page");
    if (!pageTarget?.webSocketDebuggerUrl) throw new Error("No Chrome page target found.");
    const cdp = await connect(pageTarget.webSocketDebuggerUrl);
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");

    const desktop = { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false };
    const tablet = { width: 1024, height: 768, deviceScaleFactor: 1, mobile: false };
    const mobile = { width: 390, height: 844, deviceScaleFactor: 2, mobile: true };

    await loadPage(cdp, "#/rankings", desktop);
    await screenshot(cdp, `rankings_desktop_${label}.png`);
    await screenshot(cdp, `rankings_selector_desktop_${label}.png`);

    await setSelectorValues(cdp);
    await screenshot(cdp, `rankings_selector_changed_desktop_${label}.png`);
    await screenshot(cdp, `csv_export_controls_desktop_${label}.png`);

    await loadPage(cdp, "#/methodology", desktop);
    await screenshot(cdp, `methodology_desktop_${label}.png`);

    await loadPage(cdp, "#/rankings", desktop);
    const profileRoute = await firstMdProfileRoute(cdp);
    await loadPage(cdp, profileRoute, desktop);
    await screenshot(cdp, `school_profile_desktop_${label}.png`);
    await scrollToWhyThisRank(cdp);
    await screenshot(cdp, `school_profile_why_rank_desktop_${label}.png`);

    await loadPage(cdp, "#/rankings", tablet);
    await screenshot(cdp, `rankings_tablet_${label}.png`);

    await loadPage(cdp, "#/rankings", mobile);
    await screenshot(cdp, `rankings_mobile_${label}.png`);
    await setSelectorValues(cdp);
    await screenshot(cdp, `rankings_selector_changed_mobile_${label}.png`);

    await loadPage(cdp, profileRoute, mobile);
    await screenshot(cdp, `school_profile_mobile_${label}.png`);
    await scrollToWhyThisRank(cdp);
    await screenshot(cdp, `school_profile_why_rank_mobile_${label}.png`);

    cdp.close();
  } finally {
    chrome.kill("SIGTERM");
    await sleep(500);
    fs.rmSync(userDataDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
