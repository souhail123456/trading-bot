---
description: Pre-market research — catalysts, market context, trade ideas
---

You are running the pre-market research workflow. Credentials come from the local .env file.
Resolve today's date via: DATE=$(date +%Y-%m-%d).

STEP 1 — Read memory for context:
- memory/TRADING-STRATEGY.md
- tail of memory/TRADE-LOG.md
- tail of memory/RESEARCH-LOG.md

STEP 2 — Pull live account state:
  bash scripts/alpaca.sh account
  bash scripts/alpaca.sh positions
  bash scripts/alpaca.sh orders

STEP 3 — Research market context. Try Perplexity first; fall back to native WebSearch if it exits 3:
  bash scripts/perplexity.sh "<query>" for each:
  - "WTI and Brent oil price right now"
  - "S&P 500 futures premarket today"
  - "VIX level today"
  - "Top stock market catalysts today $DATE"
  - "Earnings reports today before market open"
  - "Economic calendar today CPI PPI FOMC jobs data"
  - "S&P 500 sector momentum YTD"
  - News on any currently-held ticker

STEP 4 — Write a dated entry to memory/RESEARCH-LOG.md:
- Account snapshot (equity, cash, buying power, daytrade count)
- Market context (oil, indices, VIX, today's releases)
- 2-3 actionable trade ideas WITH catalyst + entry/stop/target
- Risk factors for the day
- Decision: trade or HOLD (default HOLD — patience > activity)

STEP 5 — Notification: silent unless urgent.
  bash scripts/clickup.sh "<one line>"
