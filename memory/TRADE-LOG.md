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
**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** +$0.00 (+0.00%) | **Phase P&L:** +$0.00 (+0.00%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| — | — | — | — | — | — | — |

**Notes:** Proxy connectivity confirmed working for first time — Alpaca API returned live data successfully (equity $100,000, cash $100,000, zero positions, zero orders). No trades executed today; account remains at the $100k paper baseline with full cash. Zero positions open. Trades today: 0. Trades this week: 0/3. Tomorrow (Day 3, Friday): initiate first position scan — screen for momentum setups with tight stops, target 1–2 entries each ≤$10k, manage 3-trade weekly cap.

---

## Apr 24 — Market-Open Trades (Day 3, Thursday — first live trades)

### Trade #1 — NVDA BUY
| Field | Value |
|-------|-------|
| Date | 2026-04-24 |
| Ticker | NVDA |
| Side | BUY |
| Shares | 99 |
| Entry Price | $201.73 |
| Position Cost | $19,971.27 (19.9% of equity) |
| Stop Type | 10% trailing stop GTC |
| Initial Stop Level | $181.48 (trail from HWM $201.64) |
| Stop Order ID | f93dcc04-fb1f-44aa-a164-f576fe46161f |
| Target | $242.08 (+20%) |
| Risk per Share | $20.17 |
| Total Risk | $1,997 |
| Total Reward | $4,005 |
| R:R | 2.0:1 |
| Thesis | AI infrastructure secular momentum: Amazon's $25B Anthropic investment confirms hyperscaler AI capex acceleration; MSFT and GOOGL report after close today — positive asymmetry for NVDA (beats raise AI spend guidance, lifting NVDA; misses only clip wings not the secular trend). Materials sector #1 YTD but in opening auction; NVDA cleanest liquid entry at open with $0.04 spread. Semiconductor AI cycle intact. |
| Sector | Technology / Semiconductors |
| Catalyst | Amazon $25B Anthropic AI deal; MSFT/GOOGL earnings tonight as AI capex read-through |

### Apr 24 — Portfolio Snapshot (market open)
**Portfolio:** ~$99,987 | **Cash:** ~$80,029 | **Positions:** 1 | **Trades this week:** 1/3 | **daytrade_count:** 0

| Ticker | Shares | Entry | Current | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|---------|---------|----------------|------|
| NVDA | 99 | $201.73 | $201.60 | -0.44% | -$12.87 | 10% trail (~$181.48) |

---

---

### Apr 23 — Midday Scan
**Portfolio:** $99,981.20 | **Cash:** $80,028.73 | **Positions:** 1 | **Daytrades used:** 1/3

| Ticker | Shares | Entry | Current | Unrealized P&L | Stop | Action |
|--------|--------|-------|---------|----------------|------|--------|
| NVDA | 99 | $201.73 | $201.52 | -$20.79 (-0.10%) | 10% trail HWM $203.83 (floor $183.45) | HOLD |

**Midday Actions:** NONE
- Cut check: -0.10% vs -7.00% threshold → no cut
- Tighten check: -0.10% vs +15%/+20% thresholds → no tighten
- Thesis check: MSFT/GOOGL earnings post-close tonight — catalyst INTACT
- Trailing stop f93dcc04-fb1f-44aa-a164-f576fe46161f confirmed ACTIVE GTC

**Notes:** Position healthy, stop in place, thesis live. Awaiting MSFT/GOOGL post-close earnings as AI capex read-through catalyst. No action warranted at midday.

---

### Apr 23 — Midday Scan (Afternoon Update)
**Live data:** UNAVAILABLE — proxy 403 (cloud IP block); WebSearch fallback used
**NVDA est. price:** ~$202.50 | **Est. Unrealized P&L:** ~+$76 (+0.38%) | **Stop:** 10% trail (assumed ACTIVE GTC)

| Ticker | Shares | Entry | Est. Current | Est. Unrealized P&L | Stop | Action |
|--------|--------|-------|--------------|---------------------|------|--------|
| NVDA | 99 | $201.73 | ~$202.50 | ~+$76 (+0.38%) | 10% trail (assumed active) | HOLD |

**Afternoon Actions:** NONE
- Cut check: +0.38% vs -7.00% threshold → no cut ✓
- Tighten check: +0.38% vs +15%/+20% thresholds → no tighten ✓
- Thesis check: AI capex cycle accelerating; NVDA +21% in April; MSFT/GOOGL reporting tonight — INTACT
- Proxy 403 blocks live confirmation; stop order assumed active (confirmed at morning scan)

**Notes:** Proxy blocked (cloud IP rotation). All threshold checks clear by wide margin. Thesis strengthening — NVDA on 11-day streak. No action warranted. MSFT/GOOGL post-close tonight remains key catalyst.

---

### Apr 23 — EOD Snapshot (Day 3, Thursday)
**Portfolio:** $99,791.15 | **Cash:** $80,028.73 (80.2%) | **Day P&L:** -$208.85 (-0.21%) | **Phase P&L:** -$208.85 (-0.21%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| NVDA | 99 | $201.73 | $199.62 | -1.42% | -$208.85 (-1.05%) | $183.45 (10% trail, HWM $203.83) |

**Notes:** First full trading day with an open position. NVDA was entered this morning at $201.73 (99 shares, ~$19,971 / 20% of equity) on AI infrastructure momentum thesis — Amazon's $25B Anthropic deal + MSFT/GOOGL earnings as AI capex catalysts. NVDA closed at $199.62, down -1.42% on the day, leaving unrealized P&L at -$208.85 (-1.05% on position). The 10% trailing stop remains active GTC with HWM $203.83 and current stop floor $183.45 — position is well inside safe zone (-1.05% vs -10% stop). daytrade_count: 1. Trades today: 1 (NVDA BUY). Trades this week: 1/3. Tomorrow (Day 4, Friday): monitor NVDA at open — MSFT/GOOGL results will set the tone; if AI capex guidance strong, look for NVDA recovery. No new entries unless NVDA closes back above $201.73; hold stop. Weekly cap: 2 more trades available.
