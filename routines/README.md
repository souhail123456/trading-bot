# Cloud Routines

Paste each prompt verbatim into the corresponding Claude Code cloud routine.
Do NOT paraphrase — the env-var check block and commit-and-push step are load-bearing.

| File | Cron (America/Chicago) | Purpose |
|------|------------------------|---------|
| pre-market.md | `0 6 * * 1-5` | Research catalysts, write trade ideas |
| market-open.md | `30 8 * * 1-5` | Execute planned trades, set stops |
| midday.md | `0 12 * * 1-5` | Scan positions, cut losers, tighten stops |
| daily-summary.md | `0 15 * * 1-5` | EOD snapshot, ClickUp recap |
| weekly-review.md | `0 16 * * 5` | Weekly stats, letter grade, strategy update |

## One-time prerequisites before creating any routine
1. Install the Claude GitHub App on this repo (least-privilege: only this repo)
2. Enable **Allow unrestricted branch pushes** on each routine's environment settings
3. Add all credentials as env vars on the routine (NOT in a .env file)

## Required env vars per routine
```
ALPACA_API_KEY          (required)
ALPACA_SECRET_KEY       (required)
ALPACA_ENDPOINT         (paper: https://paper-api.alpaca.markets/v2)
ALPACA_DATA_ENDPOINT    (https://data.alpaca.markets/v2)
PERPLEXITY_API_KEY      (optional — falls back to WebSearch if unset)
PERPLEXITY_MODEL        (optional — defaults to sonar)
CLICKUP_API_KEY         (required for notifications)
CLICKUP_WORKSPACE_ID    (required — numeric)
CLICKUP_CHANNEL_ID      (required — format 4-XXXXXXX-X)
```
