// Pebble preview-machine receiver.
//
// Runs inside each Fly Machine alongside `next dev`. Three jobs, one public
// port (8080), Node built-ins only (no npm deps so the image stays slim):
//
//   1. POST /__pebble/sync   — the engine pushes source files here (auth via
//      x-pebble-secret). Files are written into /site; on the first sync we
//      lazily spawn `next dev` on :3000. Subsequent writes let Next's file
//      watcher fire Hot Module Replacement — the iframe repaints in <0.5s with
//      no rebuild.
//   2. GET  /__pebble/healthz — { ready } once next dev answers on :3000.
//   3. everything else        — reverse-proxy to next dev on :3000, passing
//      websockets through (HMR), and injecting the visual-edit bridge
//      (/site/.pebble-bridge.js, synced by the engine) into HTML responses so
//      click-to-edit works in the workspace iframe.
//
// Security: /__pebble/* requires the shared secret. The proxy path is public
// (the preview itself). No real secrets live here (the contact form no-ops
// without RESEND_API_KEY — correct for a preview).

import http from "node:http";
import net from "node:net";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const SITE_DIR = "/site";
const NEXT_PORT = 3000;
const PUBLIC_PORT = Number(process.env.PORT || 8080);
const SECRET = process.env.PEBBLE_FLEET_SECRET || "";
const BRIDGE_FILE = path.join(SITE_DIR, ".pebble-bridge.js");

let nextProc = null;

function startNextDevOnce() {
  if (nextProc) return;
  nextProc = spawn("npx", ["next", "dev", "-p", String(NEXT_PORT), "-H", "127.0.0.1"], {
    cwd: SITE_DIR,
    stdio: "inherit",
    env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
  });
  nextProc.on("exit", (code) => {
    console.log(`[receiver] next dev exited (${code}); will respawn on next sync`);
    nextProc = null;
  });
}

function unauthorized(res) {
  res.writeHead(401, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: "bad secret" }));
}

// --- sync: write pushed files, (re)start next dev -------------------------
function handleSync(req, res) {
  if (!SECRET || req.headers["x-pebble-secret"] !== SECRET) return unauthorized(res);
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      res.writeHead(400, { "content-type": "application/json" });
      return res.end(JSON.stringify({ error: "invalid json" }));
    }
    const files = Array.isArray(payload.files) ? payload.files : [];
    let written = 0;
    for (const f of files) {
      const rel = String(f.path || "").replace(/^[/\\]+/, "");
      if (!rel || rel.includes("..")) continue;
      const dest = path.join(SITE_DIR, rel);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, String(f.data ?? ""), "utf8");
      written++;
    }
    // Allow the engine to request deletions (e.g. a renamed component).
    for (const rel of payload.deleted || []) {
      const safe = String(rel).replace(/^[/\\]+/, "");
      if (!safe || safe.includes("..")) continue;
      try { fs.rmSync(path.join(SITE_DIR, safe), { force: true }); } catch {}
    }
    startNextDevOnce();
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: true, written }));
  });
}

// --- healthz: is next dev answering? --------------------------------------
function handleHealthz(res) {
  const probe = http.request(
    { host: "127.0.0.1", port: NEXT_PORT, path: "/", method: "GET", timeout: 2000 },
    (r) => {
      r.resume();
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ ready: true, status: r.statusCode }));
    },
  );
  probe.on("error", () => {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ ready: false }));
  });
  probe.on("timeout", () => { probe.destroy(); });
  probe.end();
}

// --- proxy everything else to next dev, inject bridge into HTML -----------
function handleProxy(req, res) {
  const opts = {
    host: "127.0.0.1",
    port: NEXT_PORT,
    path: req.url,
    method: req.method,
    headers: { ...req.headers, host: `127.0.0.1:${NEXT_PORT}` },
  };
  const upstream = http.request(opts, (ur) => {
    const ct = String(ur.headers["content-type"] || "");
    const isHtml = ct.includes("text/html");
    if (!isHtml) {
      res.writeHead(ur.statusCode || 502, ur.headers);
      ur.pipe(res);
      return;
    }
    // Buffer HTML so we can inject the bridge before </body>.
    const chunks = [];
    ur.on("data", (c) => chunks.push(c));
    ur.on("end", () => {
      let html = Buffer.concat(chunks).toString("utf8");
      const bridge = readBridge();
      if (bridge) {
        const tag = `<script>${bridge}</script>`;
        const i = html.toLowerCase().lastIndexOf("</body>");
        html = i === -1 ? html + tag : html.slice(0, i) + tag + html.slice(i);
      }
      const headers = { ...ur.headers };
      delete headers["content-length"];
      delete headers["content-encoding"]; // we re-emit uncompressed
      res.writeHead(ur.statusCode || 200, headers);
      res.end(html);
    });
  });
  upstream.on("error", () => {
    res.writeHead(502, { "content-type": "text/plain" });
    res.end("preview starting…");
  });
  req.pipe(upstream);
}

function readBridge() {
  try {
    return fs.readFileSync(BRIDGE_FILE, "utf8");
  } catch {
    return "";
  }
}

const server = http.createServer((req, res) => {
  if (req.url === "/__pebble/sync" && req.method === "POST") return handleSync(req, res);
  if (req.url === "/__pebble/healthz") return handleHealthz(res);
  return handleProxy(req, res);
});

// Pass HMR (and any) websockets straight through to next dev.
server.on("upgrade", (req, socket, head) => {
  const up = net.connect(NEXT_PORT, "127.0.0.1", () => {
    up.write(
      `${req.method} ${req.url} HTTP/1.1\r\n` +
        Object.entries(req.headers).map(([k, v]) => `${k}: ${v}`).join("\r\n") +
        "\r\n\r\n",
    );
    if (head && head.length) up.write(head);
    socket.pipe(up);
    up.pipe(socket);
  });
  up.on("error", () => socket.destroy());
  socket.on("error", () => up.destroy());
});

server.listen(PUBLIC_PORT, "0.0.0.0", () => {
  console.log(`[receiver] listening on :${PUBLIC_PORT} (proxying next dev :${NEXT_PORT})`);
});
