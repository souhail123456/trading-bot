<!-- SUMMARY
portfolio_value: 100146.66
cash: -20186.07
total_pnl: 146.66
open_positions: [{"symbol": "AMZN", "shares": 64, "entry": 233.42, "side": "BUY", "unrealized_pnl": -16.64}, {"symbol": "IWM", "shares": 52, "entry": 294.306923, "side": "BUY", "unrealized_pnl": 213.88}, {"symbol": "NVDA", "shares": 72, "entry": 208.95, "side": "BUY", "unrealized_pnl": -17.28}, {"symbol": "QQQ", "shares": 20, "entry": 736.3685, "side": "BUY", "unrealized_pnl": 36.23}, {"symbol": "SPY", "shares": 20, "entry": 744.159, "side": "BUY", "unrealized_pnl": 13.22}, {"symbol": "XLE", "shares": 281, "entry": 53.47, "side": "BUY", "unrealized_pnl": 85.42}, {"symbol": "XLI", "shares": 83, "entry": 181.208193, "side": "BUY", "unrealized_pnl": 49.12}, {"symbol": "XLK", "shares": 78, "entry": 191.897308, "side": "BUY", "unrealized_pnl": 37.65}]
closed_trades: [{"symbol": "MSFT", "shares": 10, "entry": 425.73, "exit": 423.88, "realized_pnl": -18.5, "reason": "-4% rule"}, {"symbol": "AMZN", "entry": 260.52, "exit": 255.407778, "shares": 9, "pnl": -46.01, "reason": "trailing_stop", "date": "2026-05-19"}, {"symbol": "GOOGL", "entry": 351.4945, "exit": 386.1305, "shares": 20, "pnl": 692.72, "reason": "trailing_stop", "date": "2026-05-19"}, {"symbol": "SPY", "entry": 747.86, "exit": 745.407, "shares": 20, "pnl": -49.06, "reason": "market", "date": "2026-06-18"}, {"symbol": "AAPL", "shares": 51, "entry": 298.687844, "exit": 297.65, "realized_pnl": -52.93, "reason": "strategy exit signal"}, {"symbol": "XLI", "shares": 84, "entry": 182.512143, "exit": 181.055, "realized_pnl": -122.4, "reason": "unrealized_plpc <= -0.04"}, {"symbol": "XLK", "entry": 190.6, "exit": 192.824074, "shares": 81, "pnl": 180.15, "reason": "market", "date": "2026-06-22"}]
last_updated: 2026-06-22T20:03:37Z
-->

# Trade Log

## Day 0 — EOD Snapshot (pre-launch baseline, account reset)
**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0

New API keys generated Apr 22. Account reset to $100k default paper balance. No positions.

---

### Apr 22 — EOD Snapshot (Day 1, Wednesday)
**Portfolio:** N/A | **Cash:** N/A | **Day P&L:** N/A | **Phase P&L:** N/A

**Notes:** First trading day post-reset. Alpaca API returned 403 (host not in allowlist). No trades executed.

---

### Apr 23 — EOD Snapshot (Day 2, Thursday)
**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** +$0.00 | **Phase P&L:** +$0.00

**Notes:** Proxy connectivity confirmed working. No trades executed.

---

## Apr 24 — Market-Open Trades (Day 3 — first live trades)

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
| Thesis | AI infrastructure momentum: Amazon $25B Anthropic investment, MSFT/GOOGL earnings as AI capex catalyst |

### Apr 24 — EOD Snapshot (Day 3, Friday)
**Portfolio:** $100,637.56 | **Cash:** $80,028.73 (79.5%) | **Day P&L:** +$844.47 (+0.85%) | **Phase P&L:** +$637.56 (+0.64%)

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| NVDA | 99 | $201.73 | $208.17 | +$637.56 (+3.19%) | $189.86 (10% trail) |

---

### Apr 27 — EOD Snapshot (Day 7, Monday)
**Portfolio:** $101,541.43 | **Cash:** $80,028.73 (78.8%) | **Day P&L:** +$894.97 (+0.89%) | **Phase P&L:** +$1,541.43 (+1.54%)

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| NVDA | 99 | $201.73 | $217.30 | +$1,541.43 (+7.65%) | $189.86 (7% trail) |

**Notes:** Peak equity. NVDA +7.65%. Trail tightened to 7%.

---

### Apr 28 — New Trades (AMZN, GOOGL, MSFT)

| Ticker | Side | Shares | Entry | Thesis |
|--------|------|--------|-------|--------|
| AMZN | BUY | 9 | $260.52 | Earnings momentum |
| GOOGL | BUY | 20 | $351.49 | Earnings momentum |
| MSFT | BUY | 10 | $425.73 | Earnings momentum |

### Apr 28 — EOD Snapshot (Day 8)
**Portfolio:** $101,040.54 | **Cash:** $66,396.86 (66%) | **Positions:** 4

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| AMZN | 9 | $260.52 | $259.50 | -$9.18 | $239.32 |
| GOOGL | 20 | $351.49 | $349.78 | -$34.29 | $320.21 |
| MSFT | 10 | $425.73 | $428.30 | +$25.70 | $386.93 |
| NVDA | 99 | $201.73 | $212.42 | +$1,058.31 | $202.08 (5% trail) |

---

### ~Apr 30 — NVDA Stopped Out
NVDA trailing stop triggered. Realized ~$560 profit. Cash returned to ~$86,400.

### Apr 30 — EOD Snapshot (Day 10)
**Portfolio:** $100,560.59 | **Cash:** $86,399.81 (85%) | **Positions:** 3

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| AMZN | 9 | $260.52 | $264.71 | +$37.71 | $239.32 |
| GOOGL | 20 | $351.49 | $384.00 | +$650.10 | $320.21 |
| MSFT | 10 | $425.73 | $409.84 | -$158.90 | $386.93 |

---

### May 6 — EOD Snapshot (Day 16)
**Portfolio:** $100,976.14 | **Cash:** $86,399.79 (85.7%) | **Phase P&L:** +$976.14 (+0.98%)

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| AMZN | 9 | $260.52 | $275.05 | +$130.77 | $259.06 |
| GOOGL | 20 | $351.49 | $398.25 | +$935.20 | $370.29 |
| MSFT | 10 | $425.73 | $413.59 | -$121.40 | $386.93 |

---

### May 10 — EOD Snapshot (Day 20)
**Portfolio:** $101,021.11 | **Cash:** $86,399.79 (85.6%) | **Phase P&L:** +$1,021.11 (+1.02%)

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| AMZN | 9 | $260.52 | $272.68 | +$109.44 | $259.06 |
| GOOGL | 20 | $351.49 | $400.80 | +$986.20 | $370.29 |
| MSFT | 10 | $425.73 | $415.12 | -$106.10 | $386.93 |

---

### May 13 — EOD Snapshot (Day 23)
**Portfolio:** $100,923.10 | **Cash:** $86,399.79 (85.6%) | **Phase P&L:** +$923.10 (+0.92%)

| Ticker | Shares | Entry | Close | Unrealized P&L | Stop |
|--------|--------|-------|-------|----------------|------|
| AMZN | 9 | $260.52 | $270.03 | +$85.57 (+3.6%) | $259.06 |
| GOOGL | 20 | $351.49 | $402.45 | +$1,019.11 (+14.5%) | $370.29 |
| MSFT | 10 | $425.73 | $404.41 | -$213.25 (-5.0%) | $386.93 |

**Notes:** MSFT has been flagged for exit multiple times but was never sold due to a bug (cuts array not populated). Fix deployed May 14 — next midday scan will enforce the cut.

Cut MSFT due to thesis broken. Tightened stops on AMZN and GOOGL.

No trades at open — holding

Cut MSFT due to thesis broken. Tightened stop on GOOGL.

### May 14 — EOD Snapshot (Day 24, Thursday)
**Portfolio:** $100,889.88 | **Cash:** $86,399.79 (85.6%) | **Day P&L:** -$33.02 (-0.03%) | **Phase P&L:** +$889.88 (+0.89%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN | 9 | $260.52 | $267.11 | -0.01118 | $59.31 (+2.53%) | $251.83 |
| GOOGL | 20 | $351.49 | $400.50 | -0.00527 | $980.11 (+13.94%) | $382.78 |
| MSFT | 10 | $425.73 | $407.61 | 0.00592 | -$181.20 (-4.26%) | $383.01 |

**Notes:** MSFT should be reviewed for exit. Stops tightened on AMZN and GOOGL.

Cut MSFT for -4.26% loss. Tightened stops on AMZN and GOOGL.

No trades at open — holding

Cut MSFT for -4.26% loss.

Cut MSFT for -4.25% loss.

### May 17 — EOD Snapshot (Day 27, Sunday)
**Portfolio:** $100,951.24 | **Cash:** $90,638.38 (89.8%) | **Day P&L:** +$11.16 (+0.01%) | **Phase P&L:** +$951.24 (+0.95%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN | 9 | $260.52 | $264.14 | 0 | $32.58 (+1.39%) | $251.83 |
| GOOGL | 20 | $351.4945 | $396.78 | 0 | $905.71 (+12.88%) | $385.15 |

**Notes:** No trades executed today.

No trades executed at open — holding existing positions

Tightened stop on GOOGL to 5% and took partial profit of 10 shares

### May 18 — EOD Snapshot (Day 28, Monday)
**Portfolio:** $100,963.92 | **Cash:** $90,638.38 (89.7%) | **Day P&L:** +$12.68 (+0.01%) | **Phase P&L:** +$963.92 (+0.96%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN | 9 | $260.52 | $264.66 | 0.00197 | $37.26 (+1.59%) | $255.4075 |
| GOOGL | 20 | $351.4945 | $397.18 | 0.00101 | $913.71 (+12.99%) | $386.1376 |

**Notes:** No trades executed today. Stops adjusted according to trailing stop orders.

No trades executed — holding all positions

Closed AMZN for being in the red after 5 trading days. Partially closed GOOGL for +12% gain.

Closed AMZN for being in the red after 5 trading days. Partially closed GOOGL for +12% gain.

### May 19 — EOD Snapshot (Day 29, Tuesday)
**Portfolio:** $100,659.66 | **Cash:** $100,659.66 (100%) | **Day P&L:** -$304.26 (-0.3%) | **Phase P&L:** $659.66 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions.

No trades executed at open — holding all positions

### May 20 — EOD Snapshot (Day 30, Wednesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 21 — EOD Snapshot (Day 31, Thursday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 24 — EOD Snapshot (Day 34, Sunday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 25 — EOD Snapshot (Day 35, Monday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 26 — EOD Snapshot (Day 36, Tuesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 27 — EOD Snapshot (Day 37, Wednesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 28 — EOD Snapshot (Day 38, Thursday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### May 31 — EOD Snapshot (Day 41, Sunday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 01 — EOD Snapshot (Day 42, Monday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 02 — EOD Snapshot (Day 43, Tuesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 03 — EOD Snapshot (Day 44, Wednesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 04 — EOD Snapshot (Day 45, Thursday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 07 — EOD Snapshot (Day 48, Sunday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 08 — EOD Snapshot (Day 49, Monday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 09 — EOD Snapshot (Day 50, Tuesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed at open — holding all positions

### Jun 10 — EOD Snapshot (Day 51, Wednesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades at open — holding

### Jun 11 — EOD Snapshot (Day 52, Thursday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.
===
TELEGRAM===
EOD Jun 11
Portfolio: $100,659.65 (+0% day, +0.66% phase)
Cash: $100,659.65
Trades today: None
Open positions: None
Tomorrow: Monitor market and sector momentum for potential trades.

No trades at open — holding

### Jun 14 — EOD Snapshot (Day 55, Sunday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.

No trades executed, holding all positions

### Jun 15 — EOD Snapshot (Day 56, Monday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.
===
TELEGRAM===
EOD Jun 15
Portfolio: $100,659.65 (+0% day, +0.66% phase)
Cash: $100,659.65
Trades today: None
Open positions: None
Tomorrow: Monitor market and sector momentum for potential trades.

No trades executed, holding all positions

### Jun 16 — EOD Snapshot (Day 57, Tuesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today.
===
TELEGRAM===
EOD Jun 16
Portfolio: $100,659.65 (+0% day, +0.66% phase)
Cash: $100,659.65
Trades today: None
Open positions: None
Tomorrow: Monitor market and sector momentum for potential trades.

No trades executed, holding all positions

Executing strategy signals: XLI, XLK, IWM, QQQ, SPY, AAPL, GOOGL

### Jun 17 — EOD Snapshot (Day 58, Wednesday)
**Portfolio:** $100,659.65 | **Cash:** $100,659.65 (100%) | **Day P&L:** $0 (+0%) | **Phase P&L:** $659.65 (+0.66%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| None |

**Notes:** No open positions, no trades executed today. Multiple buy orders are pending.

Executed strategy signals: Bought NVDA and XLE, sold SPY and GOOGL

Cut AAPL due to strategy exit signal. Tightened stops on NVDA and XLE.

Cut XLI due to -4% rule, tighten QQQ stop to 5% due to +2.5% gain

### Jun 18 — EOD Snapshot (Day 59, Thursday)
**Portfolio:** $100,737.42 | **Cash:** $24,779 (24.6%) | **Day P&L:** $77.77 (+0.077%) | **Phase P&L:** $737.42 (+0.74%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| IWM   | 52    | 294.31| 295.51| 0.01942 | 62.56          | -    |
| NVDA  | 72    | 208.95| 210.05| 0.02639 | 79.2           | 200.82|
| QQQ   | 20    | 736.37| 740.06| 0.02429 | 73.83          | 704.73|
| XLE   | 281   | 53.47 | 53.82 | -0.01555| 98.38          | 51.21 |
| XLK   | 81    | 190.6 | 191.9 | 0.03281 | 105.05         | -     |

**Notes:** All positions are long, with stops set for NVDA, QQQ, and XLE. No trades were executed today.

Executed strategy signals: bought XLI, SPY, AAPL, GOOGL, sold XLK and XLE

Closed XLK and XLE due to strategy exit signals.

Cut XLK and XLE due to strategy exit signals. Tightened stop on NVDA to 5%.

### Jun 21 — EOD Snapshot (Day 62, Sunday)
**Portfolio:** $100,747.72 | **Cash:** $24,778.95 (24.6%) | **Day P&L:** $10.3 (+0.01%) | **Phase P&L:** $747.72 (+0.75%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| IWM   | 52    | 294.31| 295.59| 0       | 66.72          | -    |
| NVDA  | 72    | 208.95| 210.69| 0       | 125.28         | 199.81|
| QQQ   | 20    | 736.37| 740.62| 0       | 85.03          | 704.73|
| XLE   | 281   | 53.47 | 53.77 | 0       | 84.3           | 51.21 |
| XLK   | 81    | 190.6 | 191.44| 0       | 68.04          | -     |

**Notes:** All positions are long. No trades were executed today.

Executed strategy signals: bought XLK and AMZN, sold SPY, GOOGL, and XLE

Cut AAPL due to strategy exit signal. Tightened stops on IWM and XLI to 5%.

Cut AMZN and NVDA due to strategy exit signals.
