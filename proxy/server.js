const express = require("express");
const https = require("https");
const http = require("http");

const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(express.text({ limit: "1mb" }));

const PROXY_TOKEN = process.env.PROXY_TOKEN;
if (!PROXY_TOKEN) {
  console.error("PROXY_TOKEN env var required");
  process.exit(1);
}

// Auth middleware
function auth(req, res, next) {
  const token =
    req.headers["x-proxy-token"] ||
    req.query.token;
  if (token !== PROXY_TOKEN) {
    return res.status(401).json({ error: "unauthorized" });
  }
  next();
}

// Health check (no auth)
app.get("/health", (_req, res) => res.json({ ok: true }));

// --- Alpaca proxy ---
// Proxies: POST /alpaca/account → https://paper-api.alpaca.markets/v2/account
// Forwards APCA-API-KEY-ID and APCA-API-SECRET-KEY headers as-is
app.all("/alpaca/*", auth, (req, res) => {
  const path = req.params[0]; // everything after /alpaca/
  const base = req.headers["x-alpaca-base"] || "https://paper-api.alpaca.markets/v2";
  const url = new URL(`${base}/${path}`);

  // Forward query params
  for (const [k, v] of Object.entries(req.query)) {
    if (k !== "token") url.searchParams.set(k, v);
  }

  const headers = {};
  if (req.headers["apca-api-key-id"]) headers["APCA-API-KEY-ID"] = req.headers["apca-api-key-id"];
  if (req.headers["apca-api-secret-key"]) headers["APCA-API-SECRET-KEY"] = req.headers["apca-api-secret-key"];
  if (req.headers["content-type"]) headers["Content-Type"] = req.headers["content-type"];

  const body = req.method !== "GET" && req.method !== "HEAD" && req.body
    ? (typeof req.body === "string" ? req.body : JSON.stringify(req.body))
    : null;

  const opts = {
    hostname: url.hostname,
    port: url.port || 443,
    path: url.pathname + url.search,
    method: req.method,
    headers,
  };

  const proxy = https.request(opts, (upstream) => {
    res.status(upstream.statusCode);
    for (const [k, v] of Object.entries(upstream.headers)) {
      res.setHeader(k, v);
    }
    upstream.pipe(res);
  });

  proxy.on("error", (err) => {
    console.error("Alpaca proxy error:", err.message);
    res.status(502).json({ error: "proxy_error", detail: err.message });
  });

  if (body) proxy.write(body);
  proxy.end();
});

// --- Telegram proxy ---
// POST /telegram { bot_token, chat_id, text, parse_mode }
app.post("/telegram", auth, (req, res) => {
  const { bot_token, chat_id, text, parse_mode } = req.body;
  if (!bot_token || !chat_id || !text) {
    return res.status(400).json({ error: "missing bot_token, chat_id, or text" });
  }

  const payload = JSON.stringify({ chat_id, text, parse_mode: parse_mode || "Markdown" });
  const opts = {
    hostname: "api.telegram.org",
    path: `/bot${bot_token}/sendMessage`,
    method: "POST",
    headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(payload) },
  };

  const proxy = https.request(opts, (upstream) => {
    let data = "";
    upstream.on("data", (c) => (data += c));
    upstream.on("end", () => {
      res.status(upstream.statusCode).type("json").send(data);
    });
  });

  proxy.on("error", (err) => {
    console.error("Telegram proxy error:", err.message);
    res.status(502).json({ error: "proxy_error", detail: err.message });
  });

  proxy.write(payload);
  proxy.end();
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Proxy listening on :${PORT}`));
