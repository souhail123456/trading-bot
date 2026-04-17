# Trading Bot

Autonomous swing-trading agent built on Claude Code. Runs on a daily cron schedule
via Claude Code cloud routines. All state lives in Git.

## Quick Start

1. Copy `env.template` to `.env` and fill in your credentials (local use only).
2. Open this repo in Claude Code.
3. Run `/portfolio` to verify Alpaca connectivity.
4. Follow Part 7 of the setup guide to configure the five cloud routines.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Agent rulebook — auto-loaded every session |
| `env.template` | Credential template — copy to `.env`, never commit `.env` |
| `scripts/` | API wrappers — all external calls go through here |
| `routines/` | Cloud routine prompts — paste verbatim into the web UI |
| `.claude/commands/` | Local slash commands for ad-hoc use |
| `memory/` | Agent's persistent state — committed to main after every run |

## Five Scheduled Workflows (America/Chicago, weekdays)

| Workflow | Cron | Purpose |
|----------|------|---------|
| pre-market | `0 6 * * 1-5` | Research catalysts, write trade ideas |
| market-open | `30 8 * * 1-5` | Execute planned trades, set stops |
| midday | `0 12 * * 1-5` | Scan positions, cut losers, tighten stops |
| daily-summary | `0 15 * * 1-5` | EOD snapshot, ClickUp recap |
| weekly-review | `0 16 * * 5` | Weekly stats, letter grade, strategy update |

## Strategy (hard rules)

Stocks only. No options. Max 6 positions, 20% per position, 3 trades/week.
10% trailing stop on every position. Cut losers at -7%. Patience > activity.

See `memory/TRADING-STRATEGY.md` for the full rulebook.
