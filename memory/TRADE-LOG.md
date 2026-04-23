# Trade Log

## Day 0 — EOD Snapshot (pre-launch baseline, account reset)
**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0

New API keys generated Apr 22. Account reset to $100k default paper balance. No positions.

---

### Apr 22 — EOD Snapshot (Day 1, Wednesday)
**Portfolio:** N/A | **Cash:** N/A | **Day P&L:** N/A | **Phase P&L:** N/A

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| — | — | — | — | — | — | — |

**Notes:** First trading day post-reset. Alpaca API returned 403 (host not in allowlist) — live portfolio data unavailable for this snapshot. No trades executed today; account remains at the $100k paper baseline with full cash. Zero positions open. Need to resolve Alpaca IP allowlist restriction before market open tomorrow before any trading activity can resume.

---

### Apr 23 — EOD Snapshot (Day 2, Thursday)
**Portfolio:** N/A | **Cash:** N/A | **Day P&L:** N/A | **Phase P&L:** N/A

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| — | — | — | — | — | — | — |

**Notes:** Alpaca API returned 403 again — PROXY_URL env var not set so all calls hit Alpaca directly and are blocked. No trades executed; account presumed at $100k paper baseline with full cash. Zero positions open. Trades this week: 0/3. Root cause: Railway proxy credentials (PROXY_URL, PROXY_TOKEN) must be configured in the environment to bypass the IP block. No trading activity possible until proxy is wired up.
