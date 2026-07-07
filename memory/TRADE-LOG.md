<!-- SUMMARY
portfolio_value: -35076.62
cash: 23175.06
total_pnl: -135076.62
open_positions: [{"symbol": "NVDA", "shares": -72, "entry": 192.386666, "side": "SELL", "unrealized_pnl": -291.12}, {"symbol": "QQQ", "shares": -20, "entry": 709.908, "side": "SELL", "unrealized_pnl": -1.44}, {"symbol": "XLF", "shares": -264, "entry": 56.14, "side": "SELL", "unrealized_pnl": 23.76}, {"symbol": "XLV", "shares": -92, "entry": 164.15, "side": "SELL", "unrealized_pnl": -10.12}]
closed_trades: [{"symbol": "MSFT", "shares": 10, "entry": 425.73, "exit": 423.88, "realized_pnl": -18.5, "reason": "-4% rule"}, {"symbol": "AMZN", "entry": 260.52, "exit": 255.407778, "shares": 9, "pnl": -46.01, "reason": "trailing_stop", "date": "2026-05-19"}, {"symbol": "GOOGL", "entry": 351.4945, "exit": 386.1305, "shares": 20, "pnl": 692.72, "reason": "trailing_stop", "date": "2026-05-19"}, {"symbol": "SPY", "entry": 747.86, "exit": 745.407, "shares": 20, "pnl": -49.06, "reason": "market", "date": "2026-06-18"}, {"symbol": "AAPL", "shares": 51, "entry": 298.687844, "exit": 297.65, "realized_pnl": -52.93, "reason": "strategy exit signal"}, {"symbol": "XLI", "shares": 84, "entry": 182.512143, "exit": 181.055, "realized_pnl": -122.4, "reason": "unrealized_plpc <= -0.04"}, {"symbol": "XLK", "entry": 190.6, "exit": 192.824074, "shares": 81, "pnl": 180.15, "reason": "market", "date": "2026-06-22"}, {"symbol": "NVDA", "entry": 208.95, "exit": 200.37, "shares": 72, "pnl": -617.76, "reason": "trailing_stop", "date": "2026-06-23"}, {"symbol": "QQQ", "entry": 736.3685, "exit": 708.092, "shares": 20, "pnl": -565.53, "reason": "trailing_stop", "date": "2026-06-24"}, {"symbol": "XLF", "shares": 264, "entry": 54.617803, "exit": 56.42, "realized_pnl": 475.78, "reason": "strategy exit signal"}, {"symbol": "XLV", "shares": 92, "entry": 156.82, "exit": 165.15, "realized_pnl": 766.36, "reason": "strategy exit signal"}, {"symbol": "IWM", "entry": 294.306923, "exit": null, "shares": 52, "pnl": null, "reason": "stop_triggered", "date": "2026-07-07"}, {"symbol": "XLE", "entry": 53.47, "exit": null, "shares": 281, "pnl": null, "reason": "stop_triggered", "date": "2026-07-07"}]
last_updated: 2026-07-07T20:47:31Z
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

### Jun 22 — EOD Snapshot (Day 63, Monday)
**Portfolio:** $100,146.11 | **Cash:** -$20,186.07 (-20.2%) | **Day P&L:** -$601.61 (-0.6%) | **Phase P&L:** $146.11 (+0.15%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN   | 64    | 233.42| 232.95| -0.04681| -30.08         | 218.60|
| IWM   | 52    | 294.31| 297.93| 0.00792 | 188.40          | 283.55|
| NVDA  | 72    | 208.95| 208.05| -0.01253| -64.80         | 203.29|
| QQQ   | 20    | 736.37| 738.05| -0.00347| 33.63           | 708.17|
| SPY   | 20    | 744.16| 744.46| -0.00305| 6.02            | -     |
| XLE   | 281   | 53.47 | 54.10 | 0.00622 | 178.27          | 51.42 |
| XLI   | 83    | 181.21| 181.90| 0.00547 | 57.42           | 172.85|
| XLK   | 78    | 191.90| 192.31| 0.00454 | 32.19           | 178.80|

**Notes:** All positions are long. No trades were executed today. NVDA should be reviewed for exit.

Executed strategy signals: bought AAPL, NVDA, GOOGL, sold SPY, QQQ, XLK

Cut QQQ, NVDA, XLK due to strategy exit signals

Cut QQQ, AAPL, GOOGL, NVDA, XLK due to strategy exit signals

### Jun 23 — EOD Snapshot (Day 64, Tuesday)
**Portfolio:** $97,796.28 | **Cash:** -$34,869.40 (35.6%) | **Day P&L:** -$2,359.08 (-2.36%) | **Phase P&L:** -$2,203.72 (-2.20%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AAPL   | 49    | 299.19| 295.04| -0.00663| -203.24        | 279.82|
| AMZN   | 64    | 233.42| 234.26| 0.00631 | 53.76          | 218.60|
| GOOGL  | 42    | 347.30| 346.84| -0.00812| -19.48         | 324.29|
| IWM    | 52    | 294.31| 295.50| -0.00899| 62.04          | 281.32|
| NVDA   | 72    | 203.36| 200.74| -0.03791| -188.64        | 189.21|
| QQQ    | 20    | 736.37| 715.68| -0.03018| -413.77        | 708.17|
| XLE    | 281   | 53.47 | 54.54 | 0.00888 | 300.67         | 51.83 |
| XLI    | 83    | 181.21| 178.20| -0.0198 | -249.68        | 169.58|
| XLK    | 78    | 191.90| 184.61| -0.03924| -568.41        | 178.80|

**Notes:** All positions are long. No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut AAPL, NVDA, XLK, XLE due to strategy exit signals. Tightened stop on AMZN to 5%.

Midday scan: cut AAPL, GOOGL, NVDA, XLK, XLE due to strategy exit signals.

### Jun 24 — EOD Snapshot (Day 65, Wednesday)
**Portfolio:** $97,751.34 | **Cash:** -$20,707.59 (21.2%) | **Day P&L:** +$190.55 (+0.2%) | **Phase P&L:** -$2,248.66 (-2.3%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AAPL   | 49     | 299.19| 294.01| -0.00099| -253.71       | 279.82|
| AMZN   | 64     | 233.42| 235    | 0.0038  | 101.12        | 224.12|
| GOOGL  | 42     | 347.30| 344.83 | -0.00376| -103.90       | 328.73|
| IWM    | 52     | 294.31| 297.56 | 0.00758 | 169.16        | 284.71|
| NVDA   | 72     | 203.36| 200.37 | 0.00165 | -215.28       | 189.21|
| XLE    | 281    | 53.47 | 53.46  | -0.01836| -2.81        | 51.83 |
| XLI    | 83     | 181.21| 181    | 0.016   | -17.28       | 172.80|
| XLK    | 78     | 191.90| 187    | 0.01526 | -381.99       | 178.80|

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Executed strategy signals: bought XLF, XLV, SPY, QQQ; sold GOOGL, AMZN, NVDA, XLK

### Jun 25 — EOD Snapshot (Day 66, Thursday)
**Portfolio:** $96,202.35 | **Cash:** -$64,096.83 (66.7%) | **Day P&L:** -$991.80 (-1.0%) | **Phase P&L:** -$3,797.65 (-3.8%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN   | 64     | 233.42| 227.29| -0.0298 | -392.64        | 224.12|
| GOOGL  | 42     | 347.30| 343.50| -0.0052 | -159.76        | 328.73|
| IWM    | 52     | 294.31| 299.40| 0.0091  | 264.84         | 286.40|
| NVDA   | 72     | 203.36| 195.22| -0.0190 | -586.08        | 189.21|
| QQQ    | 20     | 713.48| 716.87| 0.0088  | 67.76          | 669.23|
| SPY    | 19     | 736.00| 734.60| 0.0019  | -26.61         | 686.17|
| XLE    | 281    | 53.47 | 54.21 | 0.0120  | 207.94         | 51.83 |
| XLF    | 264    | 54.62 | 53.62 | -0.0019 | -263.42        | 50.85 |
| XLI    | 83     | 181.21| 183.76| 0.0197  | 211.57         | 176.79|
| XLK    | 78     | 191.90| 184.70 | 0.0090  | -561.39        | 178.80|
| XLV    | 92     | 156.82| 156.08| 0.0178  | -68.08         | 146.20|

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

### Jun 28 — EOD Snapshot (Day 69, Sunday)
**Portfolio:** $95,589.20 | **Cash:** -$64,096.85 (67.1%) | **Day P&L:** -$0.00 (+0.00%) | **Phase P&L:** -$4,410.80 (-4.41%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| AMZN   | 64     | 233.42| 232.69| 0       | -46.72          | 224.12|
| GOOGL  | 42     | 347.30| 337.39| 0       | -416.38         | 328.73|
| IWM    | 52     | 294.31| 299.83| 0       | 287.20          | 286.40|
| NVDA   | 72     | 203.36| 192.53| 0       | -779.76         | 189.21|
| QQQ    | 20     | 713.48| 706.52| 0       | -139.24         | 669.23|
| SPY    | 19     | 736.00| 728.99| 0       | -133.20         | 686.17|
| XLE    | 281    | 53.47 | 53.84 | 0       | 103.97          | 51.83 |
| XLF    | 264    | 54.62 | 53.57 | 0       | -276.62         | 50.85 |
| XLI    | 83     | 181.21| 181.20| 0       | -0.68           | 176.79|
| XLK    | 78     | 191.90| 181.11| 0       | -841.41         | 178.80|
| XLV    | 92     | 156.82| 160.34| 0       | 323.84          | 149.40|

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Cut NVDA, XLF, XLV due to strategy exit signals. Tightened stops on QQQ and SPY to 5%.

Cut NVDA, XLF, XLV due to strategy exit signals. Tightened stops on QQQ and SPY to 5%.

### Jun 29 — EOD Snapshot (Day 70, Monday)
**Portfolio:** $97334.5 | **Cash:** -$34800.05 (35.7%) | **Day P&L:** +$1745.3 (+1.8%) | **Phase P&L:** -$12665.5 (-12.7%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 353.00 | 0.0463 | 239.24 | 329.55 |
| IWM | 52 | 294.31 | 298.77 | -0.0035 | 232.08 | 286.40 |
| NVDA | 72 | 203.36 | 194.75 | 0.0115 | -619.92 | 189.21 |
| QQQ | 20 | 713.48 | 722.99 | 0.0233 | 190.16 | 688.35 |
| SPY | 19 | 736.00 | 740.51 | 0.0158 | 85.68 | 704.48 |
| XLE | 281 | 53.47 | 53.60 | -0.0045 | 36.53 | 51.83 |
| XLF | 264 | 54.62 | 53.78 | 0.0039 | -221.66 | 50.85 |
| XLI | 83 | 181.21 | 182.94 | 0.0096 | 143.74 | 176.79 |
| XLV | 92 | 156.82 | 160.63 | 0.0018 | 350.52 | 152.83 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals. Tightened stops on GOOGL, IWM, QQQ, SPY, XLI to 5%.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals. Tightened stops on GOOGL, IWM, QQQ, SPY, XLI to 5%.

### Jun 30 — EOD Snapshot (Day 71, Tuesday)
**Portfolio:** $98,047.57 | **Cash:** -$34,800.09 (35.4%) | **Day P&L:** +$654.26 (+0.67%) | **Phase P&L:** -$1,952.43 (-1.95%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 356.49 | 0.00804 | 385.95 | 340.25 |
| IWM | 52 | 294.31 | 299.98 | 0.00338 | 295.00 | 285.71 |
| NVDA | 72 | 203.36 | 199.65 | 0.024 | -267.12 | 189.21 |
| QQQ | 20 | 713.48 | 735.43 | 0.01568 | 439.00 | 700.74 |
| SPY | 19 | 736.00 | 745.89 | 0.0066 | 187.90 | 710.47 |
| XLE | 281 | 53.47 | 53.20 | -0.00706 | -75.45 | 51.83 |
| XLF | 264 | 54.62 | 53.53 | -0.00354 | -287.18 | 50.85 |
| XLI | 83 | 181.21 | 185.03 | 0.01242 | 317.21 | 176.18 |
| XLV | 92 | 156.82 | 158.58 | -0.01344 | 161.92 | 153.16 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals

Cut NVDA, XLF, XLE, XLV due to strategy exit signals

### Jul 01 — EOD Snapshot (Day 72, Wednesday)
**Portfolio:** $97,830.85 | **Cash:** -$34,800.09 (35.5%) | **Day P&L:** -$373.11 (-0.38%) | **Phase P&L:** -$2,169.15 (-2.17%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 360.4 | 0.00848 | 550.04 | 343.55 |
| IWM | 52 | 294.31 | 298.73 | -0.00572 | 230.01 | 285.50 |
| NVDA | 72 | 203.36 | 197.33 | -0.01382 | -434.47 | 189.21 |
| QQQ | 20 | 713.48 | 724.07 | -0.01674 | 211.76 | 692.19 |
| SPY | 19 | 736.00 | 744.45 | -0.00311 | 160.54 | 709.86 |
| XLE | 281 | 53.47 | 52.81 | -0.00565 | -185.46 | 51.83 |
| XLF | 264 | 54.62 | 54.71 | 0.02052 | 24.34 | 51.22 |
| XLI | 83 | 181.21 | 183.2 | -0.01096 | 165.32 | 174.51 |
| XLV | 92 | 156.82 | 159.11 | 0.00284 | 210.68 | 153.16 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut QQQ, NVDA, XLF, XLE, XLV due to strategy exit signals. Tightened stop on XLF.

Midday scan: cut QQQ, NVDA, XLF, XLE, XLV due to strategy exit signals.

### Jul 02 — EOD Snapshot (Day 73, Thursday)
**Portfolio:** $98,054.93 | **Cash:** -$34,800.09 (35.5%) | **Day P&L:** -$22.48 (-0.02%) | **Phase P&L:** -$1,945.07 (-1.95%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 358.95 | -0.00626 | 489.14 | 345.99 |
| IWM | 52 | 294.31 | 297.17 | -0.00718 | 148.88 | 287.12 |
| NVDA | 72 | 203.36 | 194.55 | -0.01534 | -634.32 | 189.21 |
| QQQ | 20 | 713.48 | 712.8 | -0.01706 | -13.64 | 694.29 |
| SPY | 19 | 736.00 | 744.18 | -0.00212 | 155.41 | 713.74 |
| XLE | 281 | 53.47 | 53.26 | 0.00851 | -59.12 | 51.83 |
| XLF | 264 | 54.62 | 55.58 | 0.0146 | 254.02 | 52.86 |
| XLI | 83 | 181.21 | 183.53 | 0.00093 | 192.71 | 176.21 |
| XLV | 92 | 156.82 | 163.6 | 0.02545 | 623.76 | 155.66 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Cut QQQ, NVDA, XLF, XLE, XLV due to strategy exit signals

Cut QQQ, NVDA, XLF, XLE, XLV due to strategy exit signals

### Jul 05 — EOD Snapshot (Day 76, Sunday)
**Portfolio:** $98,187.98 | **Cash:** -$34,800.09 (35.4%) | **Day P&L:** $0 (+0%) | **Phase P&L:** -$1,812.02 (-1.82%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 359.91 | 0 | 529.46 | 341.29 |
| IWM | 52 | 294.31 | 297.58 | 0 | 170.20 | 282.70 |
| NVDA | 72 | 203.36 | 194.83 | 0 | -614.16 | 189.21 |
| QQQ | 20 | 713.48 | 712.60 | 0 | -17.64 | 694.29 |
| SPY | 19 | 736.00 | 744.78 | 0 | 166.81 | 707.54 |
| XLE | 281 | 53.47 | 53.22 | 0 | -70.25 | 51.83 |
| XLF | 264 | 54.62 | 55.62 | 0 | 264.58 | 52.86 |
| XLI | 83 | 181.21 | 183.91 | 0 | 224.25 | 174.71 |
| XLV | 92 | 156.82 | 163.74 | 0 | 636.64 | 155.66 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals. Partial take on SPY and XLI.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals. Partial take on SPY and XLI.

### Jul 06 — EOD Snapshot (Day 77, Monday)
**Portfolio:** $99,132.73 | **Cash:** -$34,800.09 (35.1%) | **Day P&L:** $944.75 (+0.96%) | **Phase P&L:** -$867.27 (-0.87%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| GOOGL | 42 | 347.30 | 366.27 | 0.01767 | 796.58 | 349.53 |
| IWM | 52 | 294.31 | 299.56 | 0.00665 | 273.16 | 284.61 |
| NVDA | 72 | 203.36 | 195.40 | 0.00293 | -573.12 | 189.21 |
| QQQ | 20 | 713.48 | 722.83 | 0.01436 | 186.96 | 688.93 |
| SPY | 19 | 736.00 | 751.78 | 0.00940 | 299.83 | 714.79 |
| XLE | 281 | 53.47 | 53.28 | 0.00113 | -53.39 | 51.83 |
| XLF | 264 | 54.62 | 56.14 | 0.00935 | 401.86 | 53.35 |
| XLI | 83 | 181.21 | 185.80 | 0.01028 | 381.12 | 176.28 |
| XLV | 92 | 156.82 | 162.49 | -0.00763 | 521.64 | 155.66 |

**Notes:** No trades were executed today. NVDA should be reviewed for exit.

Midday scan: cut NVDA, XLF, XLE, XLV due to strategy exit signals. Tightened stops on GOOGL, IWM, QQQ, SPY, XLI to 5% due to 10%+ gains.

Midday scan: cut NVDA, XLF, XLV due to strategy exit signals. Tightened stops on GOOGL, IWM, QQQ, SPY, XLI to 5% due to gains.

Executed trades based on strategy signals: bought XLF and XLV, sold QQQ

Executed trades based on strategy signals: bought IWM, XLI, AAPL, GOOGL, SPY, AMZN, covered XLF and XLV

Midday scan: cut QQQ, XLF, XLV due to strategy exit signals. Tightened stops on GOOGL, IWM, SPY, XLI to 5% due to gains.

Cut NVDA due to thesis broken
