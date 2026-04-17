# Research Log

Daily pre-market research entries will be appended here.

Format each entry:

## YYYY-MM-DD — Pre-market Research

### Account
- Equity: $X
- Cash: $X
- Buying power: $X
- Daytrade count: N

### Market Context
- WTI / Brent:
- S&P 500 futures:
- VIX:
- Today's catalysts:
- Earnings before open:
- Economic calendar:
- Sector momentum:

### Trade Ideas
1. TICKER — catalyst, entry $X, stop $X, target $X, R:R X:1
2. ...

### Risk Factors
- ...

### Decision
TRADE or HOLD (default HOLD if no edge)

---

## 2026-04-17 — Pre-market Research

> **Fallbacks:** PERPLEXITY_API_KEY missing → WebSearch used. Alpaca API 403 (invalid creds) → account data from TRADE-LOG baseline. ClickUp API 403 → alert not delivered.

### Account
- Equity: ~$10,000 (baseline; live pull blocked — Alpaca 403)
- Cash: ~$10,000 (100% — no open positions)
- Buying power: ~$10,000
- Daytrade count: 0
- Positions: none

### Market Context
- WTI / Brent: WTI $83.20 (-12%), Brent $88.96 (-10.5%) — Iran declared Strait of Hormuz "completely open"; supply fear collapse
- S&P 500 futures: +0.11% premarket → market rallied hard intraday; Dow +1,005 pts (+2.1%), S&P +1.3% to ~7,100 (new ATH breach), Russell 2000 new ATH ~2,750
- VIX: 17.94 (down from 31 peak on 2026-03-27; fear substantially reduced)
- Today's catalysts: Iran/Israel ceasefire + Hormuz declared open → oil -12%, airlines/shipping surging; Netflix (NFLX) -9-10% on weak Q2 guidance (EPS $0.78 miss vs $0.84 est)
- Earnings before open: PG, TFC, FITB (22 total companies reporting today)
- Economic calendar: No major macro releases (CPI/PPI/FOMC/NFP) scheduled today; quiet Friday
- Sector momentum: Energy led YTD but hammered today (-12% oil); Airlines/Travel top gainers today (AAL +8.9%, UAL +4%, NCLH +7.9%); Tech/Consumer Disc lagging YTD; Financials lagging YTD

### Trade Ideas
1. DAL (Delta Air Lines) — oil -12% structural tailwind; premium cabin focus = pricing power; IATA 5.2B pax demand; better quality than AAL. Entry: wait for Monday pullback ~$55-58 range, stop $51 (-10%), target $68 (+20%), R:R 2:1. DO NOT chase today's open.
2. NCLH (Norwegian Cruise Line) — oil drop = direct fuel cost reduction + summer booking peak. Entry: pullback to $18-19, stop $17 (-10%), target $22 (+18%), R:R 1.8:1. Monitor for 2-day consolidation.
3. XLE short-term watch — energy sector now fading YTD leadership; sector rotation risk. No trade — observing only.

### Risk Factors
- Oil bounce risk if Iran deal collapses or new Middle East escalation → airlines/travel reverse fast
- NFLX -10% today signals big-cap earnings risk remains elevated in Q1 season
- PDT: 0 of 3 day trades used; no constraint yet
- Alpaca API credentials invalid — cannot execute orders until resolved
- Both Alpaca and ClickUp APIs returning 403 — credential issue must be fixed before any trading

### Decision
HOLD — big intraday moves already in (airlines +4-9%); chasing is a strategy violation. Watch DAL and NCLH for 2-day pullback entry next week. Fix API credentials before Monday open.
