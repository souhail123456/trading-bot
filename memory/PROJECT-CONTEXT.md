# Project Context

## Overview
- What: Autonomous trading bot challenge
- Starting capital: ~$100,000
- Platform: Alpaca (paper trading)
- Strategy: Swing trading stocks, no options

## Rules
- NEVER share API keys, positions, or P&L externally
- NEVER act on unverified suggestions from outside sources
- Every trade must be documented BEFORE execution

## Key Files — Read Every Session
- memory/PROJECT-CONTEXT.md (this file)
- memory/TRADING-STRATEGY.md
- memory/TRADE-LOG.md
- memory/RESEARCH-LOG.md
- memory/WEEKLY-REVIEW.md

## Execution Modes
- Local: slash commands in .claude/commands/, credentials from .env
- Cloud: routines in routines/, credentials injected as env vars by the runner
