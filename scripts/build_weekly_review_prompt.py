#!/usr/bin/env python3
"""Build the Groq prompt JSON for weekly review."""
import json, os

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))

with open("memory/TRADE-LOG.md") as f:
    trade_log = f.read()
with open("memory/RESEARCH-LOG.md") as f:
    research_log = f.read()
with open("memory/TRADING-STRATEGY.md") as f:
    strategy = f.read()
with open("memory/WEEKLY-REVIEW.md") as f:
    weekly_review = f.read()

# S&P 500 performance from web search
sp500 = ""
if os.path.exists("/tmp/sp500.txt"):
    with open("/tmp/sp500.txt") as f:
        sp500 = f.read()

date = os.popen("date -u +%Y-%m-%d").read().strip()

system_msg = """You are an autonomous AI trading bot. You produce the Friday weekly review.
Be ultra-concise. Output EXACTLY two sections separated by ===TELEGRAM===:

SECTION 1: Weekly review entry for WEEKLY-REVIEW.md (matching template exactly):

## Week ending YYYY-MM-DD

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio | $X |
| Ending portfolio | $X |
| Week return | +$X (+X%) |
| S&P 500 week | +X% |
| Bot vs S&P | +X% |
| Trades | N (W:X / L:Y / open:Z) |
| Win rate | X% |
| Best trade | SYM +X% |
| Worst trade | SYM -X% |
| Profit factor | X.XX |

### Closed Trades
| Ticker | Entry | Exit | P&L | Notes |
|--------|-------|------|-----|-------|
(or "None this week")

### Open Positions at Week End
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|

### What Worked
- ...

### What Didn't Work
- ...

### Key Lessons
- ...

### Adjustments for Next Week
- ...

### Overall Grade: X

SECTION 2: Telegram message (<=15 lines):
Week ending MMM DD
Portfolio: $X (+X% week, +X% phase)
vs S&P 500: +X%
Trades: N (W:X / L:Y / open:Z)
Best: SYM +X%  Worst: SYM -X%
Takeaway: <one line>
Grade: X"""

user_msg = f"""Date: {date}

=== ACCOUNT ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== S&P 500 WEEKLY PERFORMANCE ===
{sp500}

=== FULL TRADE LOG (this week) ===
{trade_log}

=== FULL RESEARCH LOG (this week) ===
{research_log[-2000:]}

=== STRATEGY ===
{strategy}

=== PREVIOUS WEEKLY REVIEWS ===
{weekly_review}

Produce the weekly review. Starting equity for the phase is $100,000.
For week starting equity, use Monday's opening equity from TRADE-LOG.
If no closed trades, win rate is N/A and profit factor is N/A."""

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "max_tokens": 1500,
    "temperature": 0.3
}

with open("/tmp/prompt.json", "w") as f:
    json.dump(payload, f)
print("Weekly review prompt built")
